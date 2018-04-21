"use strict";
(function(angular) {
  /**
   * Maximum number of pairs the tournament service will try to parse.
   * @const
   * @type {number}
   */
  var MAX_PAIRS_PER_TOURNAMENT = 50;

  /**
   * Service to interact with the server's tournament APIs.
   *
   * @constructor
   * @name TichuTournamentService
   * @param {angular.$http} $http
   * @param {angular.$log} $log
   * @param {angular.$q} $q
   * @param {angular.$cacheFactory} $cacheFactory
   * @param {TichuTournamentStore} TichuTournamentStore
   * @ngInject
   */
  function TichuTournamentService($http, $log, $q, $cacheFactory, TichuTournamentStore) {
    /**
     * The HTTP request service injected at creation.
     *
     * @type {angular.$http}
     * @private
     */
    this._$http = $http;

    /**
     * The log service injected at creation.
     * @type {angular.$log}
     * @private
     */
    this._$log = $log;

    /**
     * The Q promise service injected at creation.
     *
     * @type {angular.$q}
     * @private
     */
    this._$q = $q;

    /**
     * The current outstanding promise to return the tournament headers from the server.
     *
     * @type {angular.$q.Promise<tichu.TournamentHeader[]>}
     * @private
     */
    this._tournamentListPromise = null;

    /**
     * The current outstanding promise(s) for loading tournaments.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._tournamentPromises = $cacheFactory("TournamentPromises");
    
    /**
     * The current outstanding promise(s) for loading tournament hand status.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._tournamentStatusPromises = $cacheFactory("TournamentStatusPromises");

    /**
     * The current outstanding promise(s) for loading hand results.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._handPromises = $cacheFactory("HandPromises");

    /**
     * The cache of tournament headers in the order they were received from the server.
     *
     * @type {tichu.TournamentHeader[]}
     * @private
     */
    this._tournamentList = null;

    /**
     * The cache of Tournament-related objects.
     *
     * @type {TichuTournamentStore}
     * @private
     */
    this._tournamentStore = TichuTournamentStore;
  }

  /**
   * Promises to return the tournament list (sans details) from the server.
   *
   * @returns {angular.$q.Promise<tichu.TournamentHeader[]>}
   */
  TichuTournamentService.prototype.getTournaments = function getTournaments() {
    var $q = this._$q;
    var $log = this._$log;
    if (this._tournamentList !== null) {
      return $q.when(this._tournamentList);
    }
    if (this._tournamentListPromise === null) {
      var self = this;
      this._tournamentListPromise = this._$http({
        method: 'GET',
        url: '/api/tournaments'
      }).then(function onSuccess(response) {
        try {
          self._tournamentList = self._parseTournamentList(response.data);
          return self._tournamentList;
        } catch (ex) {
          $log.error(
              "Malformed response from /api/tournaments (" + response.status + " " + response.statusText + "):\n"
              + ex + "\n\n"
              + JSON.stringify(response.data));
          var rejection = new tichu.RpcError();
          rejection.redirectToLogin = false;
          rejection.error = "Invalid response from server";
          rejection.detail = "The server sent confusing data for the list of tournaments.";
          return $q.reject(rejection);
        }
      }, ServiceHelpers.handleErrorIn($q, $log, "/api/tournaments")).finally(function afterResolution() {
        self._tournamentListPromise = null;
      });
    }
    return this._tournamentListPromise;
  };
  
  /**
   * Deletes a specific tournament from the server. Updating all the caches that
   * might contain it.
   * @returns {angular.$q.Promise<tichu.TournamentHeader[]>} The remaining tournaments.
   */
   TichuTournamentService.prototype.deleteTournament = function deleteTournament(tournamentId) {
     var $q = this._$q;
     var $log = this._$log;
     var path = "/api/tournaments/" + encodeURIComponent(tournamentId);
     var self = this;
     return this._$http({
        method: 'DELETE',
        url: path
      }).then(function onSuccess() {
        self._tournamentStore.deleteTournament(tournamentId);
        self._tournamentList = self._tournamentList.filter(function(header) {
          return header.id != tournamentId;
        });
        return self._tournamentList;
      }, ServiceHelpers.handleErrorIn($q, $log, path));
    }

  /**
   * Converts the given tournament header from the server into a TournamentHeader,
   * reusing a cached TournamentHeader if there is one in the cache.
   * @param {*} headerData The JSON to parse.
   * @private
   * @returns {tichu.TournamentHeader}
   */
  TichuTournamentService.prototype._parseTournamentHeader = function _parseTournamentHeader(headerData) {
    ServiceHelpers.assertType('tournament header', headerData, 'object');
    ServiceHelpers.assertType('tournament id', headerData['id'], 'string');
    ServiceHelpers.assertType('tournament name', headerData['name'], 'string');
    var header = this._tournamentStore.getOrCreateTournamentHeader(headerData['id']);
    header.name = headerData['name'];
    return header;
  };

  /**
   * Converts the given tournament list from the server into an array of TournamentHeaders,
   * reusing cached TournamentHeaders if they are in the cache.
   * @param {*} data
   * @private
   * @returns {tichu.TournamentHeader[]}
   */
  TichuTournamentService.prototype._parseTournamentList = function _parseTournamentList(data) {
    ServiceHelpers.assertType('tournament data', data, 'object');
    return ServiceHelpers.assertType('tournament list', data['tournaments'], 'array').map(
        this._parseTournamentHeader.bind(this));
  };

  /**
   * Retrieves a single tournament, calling the server only if necessary.
   * @param {string} id The ID of the tournament to be retrieved.
   * @param {boolean} refresh True to refresh the tournament even if it is in the cache.
   * @returns {angular.$q.Promise<tichu.Tournament>}
   */
  TichuTournamentService.prototype.getTournament = function getTournament(id, refresh) {
    var $q = this._$q;
    var $log = this._$log;
    if (!refresh && this._tournamentStore.hasTournament(id)) {
      return $q.when(this._tournamentStore.getOrCreateTournament(id));
    }
    if (!this._tournamentPromises.get(id)) {
      var self = this;
      var path = "/api/tournaments/" + encodeURIComponent(id);
      this._tournamentPromises.put(id, this._$http({
        method: 'GET',
        url: path
      }).then(function onSuccess(response) {
        try {
          return self._parseTournament(id, response.data);
        } catch (ex) {
          $log.error(
              "Malformed response from " + path + " (" + response.status + " " + response.statusText + "):\n"
              + ex + "\n\n"
              + JSON.stringify(response.data));
          var rejection = new tichu.RpcError();
          rejection.redirectToLogin = false;
          rejection.error = "Invalid response from server";
          rejection.detail = "The server sent confusing data for the tournament.";
          return $q.reject(rejection);
        }
      }, ServiceHelpers.handleErrorIn($q, $log, path)).finally(function afterResolution() {
        self._tournamentPromises.remove(id);
      }));
    }
    return this._tournamentPromises.get(id);
  };
  
   /**
   * Retrieves the status of all rounds and hands.
   * @param {string} id The ID of the tournament to be retrieved.
   * @returns {angular.$q.Promise<tichu.TournamentStatus>}
   */
  TichuTournamentService.prototype.getTournamentStatus = function getTournamentStatus(id) {
    var $q = this._$q;
    var $log = this._$log;
    if (!this._tournamentStatusPromises.get(id)) {
      var self = this;
      var path = "/api/tournaments/" + encodeURIComponent(id) + "/handStatus";
      this._tournamentStatusPromises.put(id, this._$http({
        method: 'GET',
        url: path
      }).then(function onSuccess(response) {
        try {
          return self._parseTournamentStatus(id, response.data);
        } catch (ex) {
          $log.error(
              "Malformed response from " + path + " (" + response.status + " " + response.statusText + "):\n"
              + ex + "\n\n"
              + JSON.stringify(response.data));
          var rejection = new tichu.RpcError();
          rejection.redirectToLogin = false;
          rejection.error = "Invalid response from server";
          rejection.detail = "The server sent confusing data for the hand status.";
          return $q.reject(rejection);
        }
      }, ServiceHelpers.handleErrorIn($q, $log, path)).finally(function afterResolution() {
        self._tournamentStatusPromises.remove(id);
      }));
    }
    return this._tournamentStatusPromises.get(id);
  };

  /**
   * Converts the given tournament hand status from the server into a TournamentStatus.
   # @param {string} id Id of the tournament whose status we are parsing
   * @param {*} data Response data with tournament hand statuses
   * @private
   * @returns {tichu.TournamentStatus}
   */
  TichuTournamentService.prototype._parseTournamentStatus = function _parseTournamentStatus(id, data) {
    var tournamentStatus = this._tournamentStore.getOrCreateTournamentStatus(id);
    tournamentStatus.roundStatus = data["rounds"].map(this._parseRoundStatus.bind(this));
    return tournamentStatus;
  }
  
  /**
   * Converts the given round hand status from the server into a RoundStatus.
   * @param {*} data
   * @private
   * @returns {tichu.RoundStatus}
   */
  TichuTournamentService.prototype._parseRoundStatus = function _parseRoundStatus(data) {
    var roundStatus = new tichu.RoundStatus();
    roundStatus.roundNo = data["round"];
    roundStatus.unscoredHands = data["unscored_hands"].map(this._parseHandIdentifier.bind(this));
    roundStatus.scoredHands = data["scored_hands"].map(this._parseHandIdentifier.bind(this));
    return roundStatus;
  }


  /**
   * Retrieves the score and calls of a specific hand.
   * @param {string} id The ID of the tournament to be retrieved.
   * @param {number} hand_no The hand number of the hand to be retrieved.
   * @param {number} ns_pair The North/South pair number
   * @param {number} ew_pair The East/West pair number
   * @returns {angular.$q.Promise<tichu.Hand>}
   */
  TichuTournamentService.prototype.getHand = function getHand(id, handNo, nsPair, ewPair) {
    var $q = this._$q;
    var $log = this._$log;
    var promiseCacheKey =
        encodeURIComponent(id) + "/" + encodeURIComponent(handNo.toString())
        + "/" + encodeURIComponent(nsPair);
    if (!this._handPromises.get(promiseCacheKey)) {
      var self = this;
      var path = "/api/tournaments/" + encodeURIComponent(id) + "/hands/" + 
        encodeURIComponent(handNo.toString()) + "/" +
        encodeURIComponent(nsPair.toString()) + "/" +
        encodeURIComponent(ewPair.toString());;
      this._handPromises.put(promiseCacheKey, this._$http({
        method: 'GET',
        url: path
      }).then(function onSuccess(response) {
        try {
          return self._parseHandScore(response.status, handNo, nsPair, ewPair, response.data);
        } catch (ex) {
          $log.error(
              "Malformed response from " + path + " (" + response.status + " " + response.statusText + "):\n"
              + ex + "\n\n"
              + JSON.stringify(response.data));
          var rejection = new tichu.RpcError();
          rejection.redirectToLogin = false;
          rejection.error = "Invalid response from server";
          rejection.detail = "The server sent confusing data for hand score.";
          return $q.reject(rejection);
        }
      }, ServiceHelpers.handleErrorIn($q, $log, path)
      ).finally(function afterResolution() {
        self._handPromises.remove(promiseCacheKey);
      }));
    }
    return this._handPromises.get(promiseCacheKey);
  };
  
  /**
   * Converts the given tournament hand status from the server into a TournamentStatus.
   * @param {*} data
   * @private
   * @returns {tichu.TournamentStatus}
   */
  TichuTournamentService.prototype._parseHandScore = function _parseHandScore(status, handNo, nsPair, ewPair, data) {
    var hand = new tichu.Hand(nsPair, ewPair, handNo);
    var handContext = 'hand score';
    if (status == 204) {
      return hand;
    }
    var score = new tichu.HandScore();
    var callData = ServiceHelpers.assertType(handContext + " calls", data['calls'], "object", true);
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
        handContext + " north/south score", data['ns_score'], "number|string");
    score.eastWestScore = ServiceHelpers.assertType(
        handContext + " east/west score", data['ew_score'], "number|string");
    score.notes = ServiceHelpers.assertType(
        handContext + " scoring notes", data['notes'], "string", true) || null;
    hand.score = score;
    return hand;
  }

  /**
   * Converts the given hand status from the server into a HandIdentifier.
   * @param {*} data
   * @private
   * @returns {tichu.HandIdentifier}
   */
  TichuTournamentService.prototype._parseHandIdentifier = function _parseHandIdentifier(data) {
    var handId = new tichu.HandIdentifier();
    handId.northSouthPair = data["ns_pair"];
    handId.eastWestPair = data["ew_pair"];
    handId.tableNo = data["table"];
    handId.handNo = data["hand"]
    return handId;
  }

  /**
   * Converts the given tournament list from the server into a Tournament, reusing a cached Tournament
   * if it is in the cache.
   * @param {string} id
   * @param {*} data
   * @private
   * @returns {tichu.Tournament}
   */
  TichuTournamentService.prototype._parseTournament = function _parseTournament(id, data) {
    ServiceHelpers.assertType('tournament data', data, 'object');
    ServiceHelpers.assertType('tournament name', data['name'], 'string');
    ServiceHelpers.assertType('tournament pair count', data['no_pairs'], 'number');
    if (data['no_pairs'] < 0
        || data['no_pairs'] > MAX_PAIRS_PER_TOURNAMENT
        || Math.floor(data['no_pairs']) !== data['no_pairs']) {
      throw new Error('tournament pair count was not an integer in the legal range');
    }
    ServiceHelpers.assertType('tournament board count', data['no_boards'], 'number');
    ServiceHelpers.assertType('tournament hand list', data['hands'], 'array', true);
    ServiceHelpers.assertType('tournament pair id list', data['pair_ids'], 'array');
    var hasScoredHands = !!data['hands'] && data['hands'].length > 0;
    ServiceHelpers.assertType('tournament player list', data['players'], 'array', true);
    var playerLists = [];
    for (var i = 0; i < data['no_pairs']; i += 1) {
      playerLists[i] = [];
    }
    if (data['players']) {
      playerLists = data['players'].reduce(function validatePlayer(collection, player, index) {
        ServiceHelpers.assertType('players[' + index + '] pair number', player['pair_no'], 'number');
        if (player['pair_no'] <= 0
            || player['pair_no'] > data['no_pairs']
            || Math.floor(player['pair_no']) !== player['pair_no']) {
          throw new Error('players[' + index + '] pair number (' + player['pair_no']
              + ') was not an integer in the legal range');
        }
        ServiceHelpers.assertType('players[' + index + '] name', player['name'], 'string', true);
        ServiceHelpers.assertType('players[' + index + '] email', player['email'], 'string', true);
        var pairIndex = player['pair_no'] - 1;
        collection[pairIndex] = collection[pairIndex] || [];
        collection[pairIndex].push({
          name: player['name'] || null,
          email: player['email'] || null
        });
        return collection;
      }, playerLists);
    }
    var tournament = this._tournamentStore.getOrCreateTournament(id);
    tournament.name = data['name'];
    tournament.noBoards = data['no_boards'];
    tournament.setNoPairs(
        data['no_pairs'],
        this._tournamentStore.getOrCreateTournamentPair.bind(this._tournamentStore, id));
    tournament.pairs.forEach(function(pair, index) {
      pair.setPairId(data['pair_ids'][index]);
      pair.setPlayers(playerLists[index]);
    });
    tournament.hasScoredHands = hasScoredHands;
    return tournament;
  };

  /**
   * Creates a new tournament on the server, and returns a promise for the resulting Tournament object.
   * @param {tichu.TournamentRequest} request
   * @returns {angular.$q.Promise<tichu.Tournament>}
   */
  TichuTournamentService.prototype.createTournament = function createTournament(request) {
    var path = "/api/tournaments";
    var $q = this._$q;
    var $log = this._$log;
    var $http = this._$http;
    var self = this;
    return this._$http({
      method: 'POST',
      url: path,
      data: request
    }).then(function onSuccess(response) {
      try {
        ServiceHelpers.assertType('created tournament data', response.data, 'object', false);
        var id = ServiceHelpers.assertType('created tournament id', response.data['id'], 'string', false);
        return self._getPairdIdsAndSaveTournament(id, request);
      } catch (ex) {
        $log.error(
            "Malformed response from " + path + " (" + response.status + " " + response.statusText + "):\n"
            + ex + "\n\n"
            + JSON.stringify(response.data));
        var rejection = new tichu.RpcError();
        rejection.redirectToLogin = false;
        rejection.error = "Invalid response from server";
        rejection.detail = "The server sent confusing data for the tournament creation.";
        return $q.reject(rejection);
      }
    }, ServiceHelpers.handleErrorIn($q, $log, path));
  };

  /**
   * Updates a tournament on the server, and returns a promise for the resulting Tournament object.
   * @param {string} id
   * @param {tichu.TournamentRequest} request
   * @returns {angular.$q.Promise<angular.$q.Promise<tichu.Tournament>>}
   */
  TichuTournamentService.prototype.editTournament = function editTournament(id, request) {
    var path = "/api/tournaments/" + encodeURIComponent(id);
    var $q = this._$q;
    var $log = this._$log;
    var $http = this._$http;
    var self = this;
    return this._$http({
      method: 'PUT',
      url: path,
      data: request
    }).then(function onSuccess() {
      var should_reload_pairids = self._tournamentStore.getOrCreateTournament(id).pairs.length < request.noPairs; 
      return should_reload_pairids ? self._getPairdIdsAndSaveTournament(id, request) : self._saveRequestedTournament(id, request, []);
    }, ServiceHelpers.handleErrorIn($q, $log, path));
  };

  /**
   * Gets pair id codes from the server and returns a promise for the resulting Tournament object.
   * @param {string} id
   * @param {tichu.TournamentRequest} request
   * @returns {angular.$q.Promise<tichu.Tournament>}
   */
  TichuTournamentService.prototype._getPairdIdsAndSaveTournament = function _getPairdIdsAndSaveTournament(id, request) {
    var ids_path = "/api/tournaments/" + encodeURIComponent(id) + "/pairids";
    var $q = this._$q;
    var $log = this._$log;
    var $http = this._$http;
    var self = this;
    return $http({
      method: 'GET',
      url: ids_path
    }).then(function onSuccess(response) {
      ServiceHelpers.assertType('received player ids', response.data, 'object', false);
      var pair_ids = ServiceHelpers.assertType('player ids', response.data['pair_ids'], 'array', false);
      return self._saveRequestedTournament(id, request, pair_ids);
    }, ServiceHelpers.handleErrorIn($q, $log, ids_path));
  }

  /**
   * Converts the given tournament request into an actual, cached tournament.
   * @param {string} id
   * @param {tichu.TournamentRequest} request
   * @param {string} pair_ids. Array of pair ids for the pairs in this tournament.
   * @returns {tichu.Tournament}
   * @private
   */
  TichuTournamentService.prototype._saveRequestedTournament = function _saveRequestedTournament(id, request, pair_ids) {
    var playerLists = [];
    for (var i = 0; i < request.noPairs; i += 1) {
      playerLists[i] = [];
    }
    playerLists = request.players.reduce(function(collection, player) {
      var pairIndex = player.pairNo - 1;
      collection[pairIndex] = collection[pairIndex] || [];
      collection[pairIndex].push({
        name: player.name || null,
        email: player.email || null
      });
      return collection;
    }, playerLists);
    var tournament = this._tournamentStore.getOrCreateTournament(id);
    tournament.name = request.name;
    tournament.noBoards = request.noBoards;
    tournament.setNoPairs(
        request.noPairs,
        this._tournamentStore.getOrCreateTournamentPair.bind(this._tournamentStore, id));
    tournament.pairs.forEach(function(pair, index) {
      pair.setPlayers(playerLists[index]);
      if (pair_ids) {
        pair.setPairId(pair_ids[index]);
      }
    });
    if (this._tournamentList !== null) {
      this._tournamentList.push(this._tournamentStore.getOrCreateTournamentHeader(id));
    }
    return tournament;
  };

  angular.module("tichu-tournament-service", ["ng", "tichu-tournament-store"])
      .service("TichuTournamentService", TichuTournamentService);
})(angular);