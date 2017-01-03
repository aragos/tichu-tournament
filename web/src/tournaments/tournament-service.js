"use strict";
(function(angular) {
  /**
   * Holder for the basics of tournament data, as received from the server.
   * @constructor
   * @name TournamentHeader
   * @param {string} id The identifier used for this tournament.
   * @param {string} name The name of this tournament.
   */
  function TournamentHeader(id, name) {
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
    this.name = name;
    Object.seal(this);
  }

  /**
   * Asserts that the given object has the given type.
   *
   * @template T
   * @param {string} context the string describing the value to put in the error message
   * @param {T} value the value to test the type of
   * @param {string} type the type to test for
   * @returns {T} the original value
   */
  function assertType(context, value, type) {
    var actualType = angular.isArray(value) ? 'array' : typeof value;
    if (actualType !== type) {
      throw new Error(context + " was " + actualType + ", not " + type);
    }
    return value;
  }

  /**
   * Converts the given tournament header from the server into a TournamentHeader.
   * @param {angular.$cacheFactory.Cache} cache
   * @param {any} header
   * @returns {TournamentHeader}
   */
  function parseTournamentHeader(cache, header) {
    assertType('tournament header', header, 'object');
    assertType('tournament id', header['id'], 'string');
    assertType('tournament name', header['name'], 'string');
    var result = cache.get(header['id']);
    if (result) {
      result.name = header['name'];
      return result;
    }
    result = new TournamentHeader(header['id'], header['name']);
    cache.put(header['id'], result);
    return result;
  }

  /**
   * Converts the given tournament list from the server into an array of TournamentHeaders.
   * @param {angular.$cacheFactory.Cache} headerCache
   * @param {any} data
   * @returns {TournamentHeader[]}
   */
  function parseTournamentList(headerCache, data) {
    assertType('tournament data', data, 'object');
    return assertType('tournament list', data['tournaments'], 'array').map(
        parseTournamentHeader.bind(null, headerCache));
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
     * The cache of tournament headers in the order they were received from the server.
     *
     * @type {TournamentHeader[]}
     * @private
     */
    this._tournamentList = null;

    /**
     * The current outstanding promise to return the tournament headers from the server.
     *
     * @type {angular.$q.Promise<TournamentHeader[]>}
     * @private
     */
    this._tournamentListPromise = null;

    /**
     * The cache of TournamentHeader instances.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._headerCache = $cacheFactory("TournamentHeaders");
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
          self._tournamentList = parseTournamentList(self._headerCache, response.data);
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
      }, function onError(response) {
        var rejection = {};
        console.log(
            "Got error calling /api/tournaments (" + response.status + " " + response.statusText + "):\n"
            + JSON.stringify(response.data));
        rejection.redirectToLogin = (response.status === 401);
        if (typeof response.data === 'object' && response.data.error && response.data.detail) {
          rejection.error = response.data.error;
          rejection.detail = response.data.detail;
        } else {
          rejection.error = response.statusText + " (" + response.status + ")";
          rejection.detail = response.data;
        }
        return $q.reject(rejection);
      }).finally(function() {
        self._tournamentListPromise = null;
      });
    }
    return this._tournamentListPromise;
  };

  angular.module("tichu-tournament-service", ["ng"])
      .service("TichuTournamentService", TichuTournamentService);
})(angular);