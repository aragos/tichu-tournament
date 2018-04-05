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
     * The current outstanding promise(s) for loading hand status.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._handStatusPromises = $cacheFactory("HandStatusPromises");

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
   * @returns {angular.$q.Promise<tichu.HandStatus>}
   */
  TichuTournamentService.prototype.getHandStatus = function getTournament(id) {
    var $q = this._$q;
    var $log = this._$log;
    if (!this._handStatusPromises.get(id)) {
      var self = this;
      var path = "/api/tournaments/" + encodeURIComponent(id) + "/unscoredHands";
      this._handStatusPromises.put(id, this._$http({
        method: 'GET',
        url: path
      }).then(function onSuccess(response) {
        try {
          return self._parseHandStatus(id, response.data);
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
        self._handStatusPromises.remove(id);
      }));
    }
    return this._handStatusPromises.get(id);
  };
  
  TichuTournamentService.prototype_parseHandStatus = function _parseHandStatus(id, data) {
    var handStatus = new tichu.HandStatus();
    handStatus.unscoredHands = [data["unscored_hands"][0]["hand"]];
    return handStatus;
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
    var self = this;
    return this._$http({
      method: 'POST',
      url: path,
      data: request
    }).then(function onSuccess(response) {
      try {
        ServiceHelpers.assertType('created tournament data', response.data, 'object', false);
        var id = ServiceHelpers.assertType('created tournament id', response.data['id'], 'string', false);
        return self._saveRequestedTournament(id, request);
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
   * @returns {angular.$q.Promise<tichu.Tournament>}
   */
  TichuTournamentService.prototype.editTournament = function editTournament(id, request) {
    var path = "/api/tournaments/" + encodeURIComponent(id);
    var $q = this._$q;
    var $log = this._$log;
    var self = this;
    return this._$http({
      method: 'PUT',
      url: path,
      data: request
    }).then(function onSuccess() {
      return self._saveRequestedTournament(id, request);
    }, ServiceHelpers.handleErrorIn($q, $log, path));
  };

  /**
   * Converts the given tournament request into an actual, cached tournament.
   * @param {string} id
   * @param {tichu.TournamentRequest} request
   * @returns {tichu.Tournament}
   * @private
   */
  TichuTournamentService.prototype._saveRequestedTournament = function _saveRequestedTournament(id, request) {
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
    });
    if (this._tournamentList !== null) {
      this._tournamentList.push(this._tournamentStore.getOrCreateTournamentHeader(id));
    }
    return tournament;
  };

  angular.module("tichu-tournament-service", ["ng", "tichu-tournament-store"])
      .service("TichuTournamentService", TichuTournamentService);
})(angular);