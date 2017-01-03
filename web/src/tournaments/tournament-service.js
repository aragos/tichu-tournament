"use strict";
(function(angular) {
  /**
   * Holder for the basics of tournament data, as received from the server when listing tournaments.
   * @constructor
   * @name TournamentHeader
   * @param {string} id The identifier used for this tournament.
   */
  function TournamentHeader(id) {
    /**
     * The identifier of this tournament.
     * @type {string}
     * @export
     */
    this.id = id;
    /**
     * The name of this tournament.
     * @type {string}
     * @export
     */
    this.name = "Unnamed Tournament";
    Object.seal(this);
  }

  /**
   * Holder for data about a player in a tournament.
   * @constructor
   */
  function TournamentPlayer() {
    /**
     * The name of this player.
     * @type {string}
     */
    this.name = "Player";
    /**
     * The email of this player.
     * @type {?string}
     */
    this.email = null;
    Object.seal(this);
  }

  /**
   * Holder for data about a single pair.
   * @param {number} pairNo
   * @name TournamentPair
   * @constructor
   */
  function TournamentPair(pairNo) {
    /**
     * The number of this pair.
     * @type {number}
     */
    this.pairNo = pairNo;
    /**
     * The players in this pair.
     * @type {TournamentPlayer[]}
     */
    this.players = [];
    Object.seal(this);
  }

  /**
   * The tournament object, containing the full details about the tournament and related objects.
   * @param {!TournamentHeader} header The header object this tournament is associated with.
   * @name Tournament
   * @constructor
   */
  function Tournament(header) {
    this._header = header;
    this.noBoards = 0;
    this.pairs = [];
    Object.seal(this);
  }

  Object.defineProperty(Tournament.prototype, "id", {
    enumerable: true,
    get: function getId() {
      return this._header.id;
    }
  });

  Object.defineProperty(Tournament.prototype, "name", {
    enumerable: true,
    get: function getName() {
      return this._header.name;
    },
    set: function setName(name) {
      this._header.name = name;
    }
  });

  Object.defineProperty(Tournament.prototype, "noPairs", {
    enumerable: true,
    get: function getNoPairs() {
      return this.pairs.length;
    },
    set: function setNoPairs(num) {
      if (num < 0 || num > 10 || Math.floor(num) !== num) {
        throw new Error("no_pairs must be an integer >= 0 and <= 10");
      }
      if (this.pairs.length > num) {
        this.pairs.splice(num);
      } else {
        while(this.pairs.length < num) {
          this.pairs.push(new TournamentPair(this.pairs.length + 1));
        }
      }
    }
  });

  /**
   * Asserts that the given object has the given type.
   *
   * @template T
   * @param {string} context the string describing the value to put in the error message
   * @param {T} value the value to test the type of
   * @param {string} type the type to test for
   * @param {boolean=} allowUndefined whether undefined is allowed
   * @returns {T} the original value
   */
  function assertType(context, value, type, allowUndefined) {
    if (allowUndefined && value === undefined) {
      return value;
    }
    var actualType = angular.isArray(value) ? 'array' : typeof value;
    if (actualType !== type) {
      throw new Error(context + " was " + actualType + ", not " + type);
    }
    return value;
  }

  /**
   * Creates an error handler for the standard API error structure.
   * @param {angular.$q} $q The promise service to reject with.
   * @param {string} path The API path that was called and failed.
   * @returns {Function} A response handler.
   */
  function handleErrorIn($q, path) {
    return function onError(response) {
      var rejection = {};
      if (typeof response.status === 'number') {
        console.log(
            "Got error calling " + path + " (" + response.status + " " + response.statusText + "):\n"
            + JSON.stringify(response.data));
        rejection.redirectToLogin = (response.status === 401);
        if (typeof response.data === 'object' && response.data.error && response.data.detail) {
          rejection.error = response.data.error;
          rejection.detail = response.data.detail;
        } else {
          rejection.error = response.statusText + " (" + response.status + ")";
          rejection.detail = response.data;
        }
      } else {
        console.log(response);
        rejection.redirectToLogin = false;
        rejection.error = "Client Error";
        rejection.detail = "Something went wrong when talking to the server...";
      }
      return $q.reject(rejection);
    }
  }

  /**
   * Service to interact with the server's tournament APIs.
   *
   * @constructor
   * @name TichuTournamentService
   * @param {angular.$http} $http
   * @param {angular.$q} $q
   * @param {angular.$cacheFactory} $cacheFactory
   * @ngInject
   */
  function TichuTournamentService($http, $q, $cacheFactory) {
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
     * The current outstanding promise to return the tournament headers from the server.
     *
     * @type {angular.$q.Promise<TournamentHeader[]>}
     * @private
     */
    this._tournamentListPromise = null;

    /**
     * The cache of tournament headers in the order they were received from the server.
     *
     * @type {TournamentHeader[]}
     * @private
     */
    this._tournamentList = null;

    /**
     * The cache of TournamentHeader instances.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._headerCache = $cacheFactory("TournamentHeaders");

    /**
     * The current outstanding promise(s) for loading tournaments.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._tournamentPromises = $cacheFactory("TournamentPromises");

    /**
     * The cache of Tournament instances.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._tournamentCache = $cacheFactory("Tournaments");
  }

  /**
   * Promises to return the tournament list (sans details) from the server.
   *
   * @returns {angular.$q.Promise<TournamentHeader[]>}
   */
  TichuTournamentService.prototype.getTournaments = function getTournaments() {
    var $q = this._$q;
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
          console.log(
              "Malformed response from /api/tournaments (" + response.status + " " + response.statusText + "):\n"
              + ex + "\n\n"
              + JSON.stringify(response.data));
          return $q.reject({
            redirectToLogin: false,
            error: "Invalid response from server",
            detail: "The list of tournaments... wasn't."
          });
        }
      }, handleErrorIn($q, "/api/tournaments")).finally(function afterResolution() {
        self._tournamentListPromise = null;
      });
    }
    return this._tournamentListPromise;
  };

  /**
   * Memoized form of the TournamentHeader constructor. Creates a new TournamentHeader if it doesn't
   * exist and then caches it, or gets one from the cache and updates its name if it did exist.
   * @param {string} id The ID of the TournamentHeader.
   * @param {string} name
   * @private
   * @returns {TournamentHeader}
   */
  TichuTournamentService.prototype._constructTournamentHeader = function _constructTournamentHeader(id, name) {
    var result = this._headerCache.get(id);
    if (!result) {
      result = new TournamentHeader(id);
      this._headerCache.put(id, result);
    }
    result.name = name;
    return result;
  };

  /**
   * Converts the given tournament header from the server into a TournamentHeader,
   * reusing a cached TournamentHeader if there is one in the cache.
   * @param {any} header
   * @private
   * @returns {TournamentHeader}
   */
  TichuTournamentService.prototype._parseTournamentHeader = function _parseTournamentHeader(header) {
    assertType('tournament header', header, 'object');
    assertType('tournament id', header['id'], 'string');
    assertType('tournament name', header['name'], 'string');
    return this._constructTournamentHeader(header['id'], header['name']);
  };

  /**
   * Converts the given tournament list from the server into an array of TournamentHeaders,
   * reusing cached TournamentHeaders if they are in the cache.
   * @param {any} data
   * @private
   * @returns {TournamentHeader[]}
   */
  TichuTournamentService.prototype._parseTournamentList = function _parseTournamentList(data) {
    assertType('tournament data', data, 'object');
    return assertType('tournament list', data['tournaments'], 'array').map(
        this._parseTournamentHeader.bind(this));
  };

  /**
   * Retrieves a single tournament, calling the server only if necessary.
   * @param {string} id The ID of the tournament to be retrieved.
   * @returns {angular.$q.Promise<Tournament>}
   */
  TichuTournamentService.prototype.getTournament = function getTournament(id) {
    var $q = this._$q;
    var cached = this._tournamentCache.get(id);
    if (cached) {
      return $q.when(cached);
    }
    if (!this._tournamentPromises.get(id)) {
      var self = this;
      var path = "/api/tournaments/" + encodeURIComponent(id);
      this._tournamentPromises.put(id, this._$http({
        method: 'GET',
        url: path
      }).then(function onSuccess(response) {
        try {
          self._parseTournament(id, response.data);
          return self._tournamentCache.get(id);
        } catch (ex) {
          console.log(
              "Malformed response from " + path + " (" + response.status + " " + response.statusText + "):\n"
              + ex + "\n\n"
              + JSON.stringify(response.data));
          return $q.reject({
            redirectToLogin: false,
            error: "Invalid response from server",
            detail: "The tournament... wasn't."
          });
        }
      }, handleErrorIn($q, path)).finally(function afterResolution() {
        self._tournamentPromises.remove(id);
      }));
    }
    return this._tournamentPromises.get(id);
  };

  /**
   * Memoized form of the Tournament constructor. Creates a new Tournament if it doesn't
   * exist and then caches it, or gets one from the cache if it did exist.
   * @param {TournamentHeader} header
   * @private
   * @returns {Tournament}
   */
  TichuTournamentService.prototype._constructTournament = function _constructTournament(header) {
    var result = this._tournamentCache.get(header.id);
    if (result) {
      return result;
    }
    result = new Tournament(header);
    this._tournamentCache.put(header.id, result);
    return result;
  };

  /**
   * Converts the given tournament list from the server into a Tournament, reusing a cached Tournament
   * if it is in the cache.
   * @param {string} id
   * @param {any} data
   * @private
   * @returns {Tournament}
   */
  TichuTournamentService.prototype._parseTournament = function _parseTournament(id, data) {
    assertType('tournament data', data, 'object');
    assertType('tournament name', data['name'], 'string');
    var header = this._constructTournamentHeader(id, data['name']);
    var tournament = this._constructTournament(header);
    assertType('tournament pair count', data['no_pairs'], 'number');
    tournament.noPairs = data['no_pairs'];
    assertType('tournament board count', data['no_boards'], 'number');
    tournament.noBoards = data['no_boards'];
    if (data['players']) {
      assertType('tournament player list', data['players'], 'array', true);
      var playerLists = data['players'].reduce(function validatePlayer(collection, player, index) {
        assertType('players[' + index + '] pair number', player['pair_no'], 'number');
        if (player['pair_no'] <= 0
            || player['pair_no'] > tournament.noPairs
            || Math.floor(player['pair_no']) !== player['pair_no']) {
          throw new Error('players[' + index + '] pair number (' + player['pair_no']
              + ') was not an integer in the legal range');
        }
        assertType('players[' + index + '] name', player['name'], 'string');
        assertType('players[' + index + '] email', player['email'], 'string', true);
        var pairIndex = player['pair_no'] - 1;
        collection[pairIndex] = collection[pairIndex] || [];
        collection[pairIndex].push(player);
        return collection;
      }, []);
      tournament.pairs.forEach(function(pair, pairIndex) {
        var playersFromData = playerLists[pairIndex] || [];
        var oldPlayers = pair.players;
        if (oldPlayers.length > playersFromData.length) {
          oldPlayers.splice(playersFromData.length);
        } else {
          while (oldPlayers.length < playersFromData.length) {
            oldPlayers.push(new TournamentPlayer());
          }
        }
        oldPlayers.forEach(function(player, playerIndex) {
          player.name = playersFromData[playerIndex]['name'];
          player.email = playersFromData[playerIndex]['email'] || null;
        });
      });
    }
    return tournament;
  };

  angular.module("tichu-tournament-service", ["ng"])
      .service("TichuTournamentService", TichuTournamentService);
})(angular);