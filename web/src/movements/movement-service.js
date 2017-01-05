"use strict";
(function(angular) {
  /**
   * Service to interact with the server's movement and scoring APIs.
   *
   * @constructor
   * @name TichuMovementService
   * @param {angular.$http} $http
   * @param {angular.$q} $q
   * @param {angular.$cacheFactory} $cacheFactory
   * @param {TichuTournamentStore} TichuTournamentStore
   * @param {TichuMovementStore} TichuMovementStore
   * @ngInject
   */
  function TichuMovementService($http, $q, $cacheFactory, TichuTournamentStore, TichuMovementStore) {
    /**
     * The HTTP request service injected at creation.
     *
     * @type {angular.$http}
     * @private
     */
    this._$http = $http;

    /**
     * The Q promise service injected at creation.
     *
     * @type {angular.$q}
     * @private
     */
    this._$q = $q;

    /**
     * The cache of Tournament-related objects.
     *
     * @type {TichuTournamentStore}
     * @private
     */
    this._tournamentStore = TichuTournamentStore;

    /**
     * The cache of Movement instances.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._movementStore = TichuMovementStore;

    /**
     * The cache of promises for Movement instances.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._movementPromiseCache = $cacheFactory("MovementPromises");
  }

  /**
   * Makes a request for the movement specified by the tournament ID and pair number.
   *
   * @param {string} tournamentId The tournament ID to get a movement from.
   * @param {number} pairNo The pair number whose movement should be retrieved.
   * @param {string=} pairCode If present, the pair code to authenticate with.
   * @returns {angular.$q.Promise<tichu.Movement>}
   */
  TichuMovementService.prototype.getMovement = function getMovement(tournamentId, pairNo, pairCode) {
    var $q = this._$q;
    if (this._movementStore.hasMovement(tournamentId, pairNo)) {
      return $q.when(this._movementStore.getOrCreateMovement(tournamentId, pairNo));
    }
    var movementPromiseCacheKey =
        encodeURIComponent(tournamentId) + "/" + encodeURIComponent(pairNo.toString())
        + "/" + encodeURIComponent(pairCode);
    if (!this._movementPromiseCache.get(movementPromiseCacheKey)) {
      var path = "/api/tournaments/" + encodeURIComponent(tournamentId)
          + "/movement/" + encodeURIComponent(pairNo.toString());
      var self = this;
      this._movementPromiseCache.put(movementPromiseCacheKey, this._$http({
        method: 'GET',
        url: path,
        headers: pairCode ? {'X-tichu-pair-code': pairCode} : {}
      }).then(function onSuccess(response) {
        try {
          return self._parseMovement(tournamentId, pairNo, response.data);
        } catch (ex) {
          console.log(
              "Malformed response from " + path + " (" + response.status + " " + response.statusText + "):\n"
              + ex + "\n\n"
              + JSON.stringify(response.data));
          return $q.reject({
            redirectToLogin: false,
            error: "Invalid response from server",
            detail: "The movement... wasn't."
          });
        }
      }, ServiceHelpers.handleErrorIn($q, path)).finally(function afterResolution() {
        self._movementPromiseCache.remove(movementPromiseCacheKey);
      }));
    }
    return this._movementPromiseCache.get(movementPromiseCacheKey);
  };

  /**
   * Translates the given JSON object into a HandScore (or null, if it was missing).
   * @param {string} handContext A string for logging errors in the score parsing.
   * @param {*} scoreData The JSON data to be parsed.
   * @private
   * @returns {?tichu.HandScore}
   */
  TichuMovementService.prototype._parseHandScore = function _parseHandScore(handContext, scoreData) {
    if (!ServiceHelpers.assertType(handContext + " score", scoreData, "object", true)) {
      return null;
    }
    var score = new tichu.HandScore();
    var callData = ServiceHelpers.assertType(handContext + " calls", scoreData['calls'], "object", true);
    if (callData) {
      score.calls = Object.keys(tichu.Position).map(function (positionKey) {
        var position = tichu.Position[positionKey];
        var call = ServiceHelpers.assertType(
            handContext + " " + position + " call", callData[position], "string", true);
        if (!call) {
          return null;
        }
        if (!tichu.isValidCall(call)) {
          throw new Error(handContext + " " + position + " call was not a valid call");
        }
        return {
          side: position,
          call: call
        };
      }).filter(function(call) {
        return call !== null;
      });
    } else {
      score.calls = [];
    }
    score.northSouthScore = ServiceHelpers.assertType(
        handContext + " north/south score", scoreData['ns_score'], "number");
    score.eastWestScore = ServiceHelpers.assertType(
        handContext + " east/west score", scoreData['ew_score'], "number");
    score.notes = ServiceHelpers.assertType(
        handContext + " scoring notes", scoreData['notes'], "string", true) || null;
    return score;
  };

  /**
   * Translates the given JSON object into a Hand.
   * @param {string} tournamentId The ID of the tournament this hand is for.
   * @param {number} nsPair The north-south pair for this hand.
   * @param {number} ewPair The east-west pair for this hand.
   * @param {string} roundContext The string context used for logging errors in parsing the hand.
   * @param {*} handData The JSON hand data to be parsed.
   * @param {number} handIndex The hand index used for logging errors in parsing the hand.
   * @returns {tichu.Hand}
   * @private
   */
  TichuMovementService.prototype._parseHand = function _parseHand(
      tournamentId, nsPair, ewPair, roundContext, handData, handIndex) {
    var handContext = roundContext + " hand[" + handIndex + "]";
    ServiceHelpers.assertType(handContext, handData, 'object');
    var handNo = ServiceHelpers.assertType(handContext + " hand number", handData['hand_no'], "number");
    if (handNo <= 0 || Math.floor(handNo) !== handNo) {
      throw new Error(handContext + " hand number was not a positive integer");
    }
    var score = this._parseHandScore(handContext, handData['score']);
    var hand = this._movementStore.getOrCreateHand(tournamentId, nsPair, ewPair, handNo);
    hand.score = score;
    return hand;
  };

  /**
   * Translates the given JSON object into a MovementRound.
   * @param {string} tournamentId The ID of the tournament this movement round is for.
   * @param {number} pairNo The pair number this movement round is for.
   * @param {*} movementRound The JSON data for the current movement round.
   * @param {number} index The number of the current movement round, for logging purposes.
   * @returns {tichu.MovementRound}
   * @private
   */
  TichuMovementService.prototype._parseMovementRound = function _parseMovementRound(
      tournamentId, pairNo, movementRound, index) {
    var context = "movement round[" + index + "]";
    ServiceHelpers.assertType(context , movementRound, "object");
    var round = new tichu.MovementRound();
    round.roundNo = ServiceHelpers.assertType(context + " round", movementRound['round'], "number");
    var position = ServiceHelpers.assertType(context + " position", movementRound['position'], "string");
    if (position.length <= 1) {
      throw new Error(context + " position was too short")
    }
    round.position = position[position.length - 1];
    round.table = position.substring(0, position.length - 1);
    if (!tichu.isValidPairPosition(round.side)) {
      throw new Error(context + " position didn't end in a valid side");
    }
    round.opponent = ServiceHelpers.assertType(context + " opponent", movementRound['opponent'], 'number');
    if (round.opponent <= 0 || Math.floor(round.opponent) !== round.opponent) {
      throw new Error(context + " opponent was not a positive integer");
    }
    round.isRelayTable = !!ServiceHelpers.assertType(
        context + " relay table", movementRound['relay_table'], "boolean");
    var nsPair, ewPair;
    if (round.position === tichu.PairPosition.NORTH_SOUTH) {
      nsPair = pairNo;
      ewPair = round.opponent;
    } else {
      nsPair = round.opponent;
      ewPair = pairNo;
    }
    ServiceHelpers.assertType(context + " hands", movementRound['hands'], 'array');
    round.hands = movementRound['hands'].map(this._parseHand.bind(this, tournamentId, nsPair, ewPair, context));
    return round;
  };

  /**
   * Converts the given deserialized JSON into a movement and caches it.
   * @param {string} tournamentId The ID of the tournament this movement is for.
   * @param {number} pairNo The number of the pair this movement is for.
   * @param {*} data The JSON data received from the server.
   * @private
   * @returns {tichu.Movement}
   */
  TichuMovementService.prototype._parseMovement = function _parseMovement(tournamentId, pairNo, data) {
    ServiceHelpers.assertType("movement data", data, "object");
    ServiceHelpers.assertType("tournament name", data["name"], "string");
    ServiceHelpers.assertType("player list", data["players"], "array", true);
    var players;
    if (data["players"]) {
      players = data["players"].map(function(playerData, index) {
        return {
          name: ServiceHelpers.assertType("players[" + index + "] name", playerData['name'], 'string', true) || null,
          email: ServiceHelpers.assertType("players[" + index + "] email", playerData['email'], 'string', true) || null
        }
      });
    }
    ServiceHelpers.assertType("round list", data["movement"], "array");
    var convertedRounds = data["movement"].map(this._parseMovementRound.bind(this, tournamentId, pairNo));
    var movement = this._movementStore.getOrCreateMovement(tournamentId, pairNo);
    movement.tournamentId.name = data["name"];
    if (players) {
      movement.pair.setPlayers(players);
    }
    movement.rounds = convertedRounds;
    return movement;
  };

  angular.module("tichu-movement-service", ["ng", "tichu-tournament-store", "tichu-movement-store"])
      .service("TichuMovementService", TichuMovementService);
})(angular);