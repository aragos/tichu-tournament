"use strict";
(function(angular) {
  /**
   * Service to interact with the server's tournament APIs.
   *
   * @constructor
   * @param {angular.$http} $http
   * @param {angular.$q} $q
   * @ngInject
   */
  function TournamentService($http, $q) {
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
     * @type {Tournament[]}
     * @private
     */
    this._tournamentList = null;

    /**
     * The current outstanding promise to return the tournament headers from the server.
     *
     * @type {angular.$q.Promise<Tournament[]>}
     * @private
     */
    this._tournamentPromise = null;
  }

  /**
   * Promises to return the tournament list (sans details) from the server.
   *
   * @returns {angular.$q.Promise<Tournament[]>}
   */
  TournamentService.prototype.getTournaments = function() {
    var $q = this._$q;
    if (this._tournamentList !== null) {
      return $q.when(this._tournamentList);
    }
    if (this._tournamentPromise === null) {
      var self = this;
      this._tournamentPromise = this._$http({
        method: 'GET',
        url: '/api/tournaments'
      }).then(function onSuccess(response) {
        if (typeof response.data !== 'object' || !angular.isArray(response.data['tournaments'])) {
          console.log(
              "Invalid response from /api/tournaments (" + response.status + " " + response.statusText + "):\n"
              + JSON.stringify(response.data));
          return $q.reject({
            redirectToLogin: false,
            error: "Invalid response from server",
            detail: "The list of tournaments... wasn't."
          });
        }
        try {
          var tournamentList = response.data['tournaments'].map(function (tournamentHeader) {
            if (typeof tournamentHeader !== 'object'
                || typeof tournamentHeader['id'] !== 'string'
                || typeof tournamentHeader['name'] !== 'string') {
              throw new Error("missing or malformed property in " + JSON.stringify(tournamentHeader))
            }
            return {
              id: tournamentHeader['id'],
              name: tournamentHeader['name']
            }
          });
        } catch (ex) {
          console.log(
              "Malformed response from /api/tournaments (" + response.status + " " + response.statusText + "):\n"
              + ex + "\n\n"
              + JSON.stringify(response.data));
          return $q.reject({
            redirectToLogin: false,
            error: "Invalid response from server",
            detail: "One of the tournaments in the list... wasn't."
          });
        }
        self._tournamentList = tournamentList;
        return self._tournamentList;
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
        self._tournamentPromise = null;
      });
    }
    return this._tournamentPromise;
  };

  angular.module("tichu-tournament-service", [])
      .service("TichuTournamentService", TournamentService);
})(angular);