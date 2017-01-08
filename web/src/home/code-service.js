"use strict";
(function(angular) {
  /**
   * Service to interact with the server's player code translation API.
   *
   * @constructor
   * @name TichuCodeService
   * @param {angular.$http} $http
   * @param {angular.$log} $log
   * @param {angular.$q} $q
   * @ngInject
   */
  function TichuCodeService($http, $log, $q) {
    /**
     * The HTTP request service injected at creation.
     *
     * @type {angular.$http}
     * @private
     */
    this._$http = $http;

    /**
     * The log service injected at creation.
     *
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
  }

  /**
   * Makes a request for the tournament ID and pair number specified by the pair code.
   *
   * @param {string} pairCode The pair code to translate into tournament ID and pair number.
   * @returns {angular.$q.Promise<{tournamentId: string, pairNo: number}>}
   */
  TichuCodeService.prototype.getMovementForCode = function getMovementForCode(pairCode) {
    var $q = this._$q;
    var $log = this._$log;
    var self = this;
    var path = "/api/tournaments/pairno/" + encodeURIComponent(pairCode);
    return this._$http({
      method: 'GET',
      url: path
    }).then(function onSuccess(response) {
      try {
        var results = self._parseCodeResponse(response.data);
        if (results.length === 1) {
          return results[0];
        } else if (results.length === 0) {
          var notEnoughTournaments = new tichu.RpcError();
          notEnoughTournaments.redirectToLogin = false;
          notEnoughTournaments.error = "No tournament found!";
          notEnoughTournaments.detail =
              "Check the pair code the tournament director gave you and try again.";
          return $q.reject(notEnoughTournaments);
        } else {
          var tooManyTournaments = new tichu.RpcError();
          tooManyTournaments.redirectToLogin = false;
          tooManyTournaments.error = "Bad luck!";
          tooManyTournaments.detail =
              "What are the odds?! There are multiple tournaments that your pair code could be for...";
          return $q.reject(tooManyTournaments);
        }
      } catch (ex) {
        $log.error(
            "Malformed response from " + path + " (" + response.status + " " + response.statusText + "):\n"
            + ex + "\n\n"
            + JSON.stringify(response.data));
        var invalidData = new tichu.RpcError();
        invalidData.redirectToLogin = false;
        invalidData.error = "Invalid response from server";
        invalidData.detail = "The server sent confusing data about the pair code.";
        return $q.reject(invalidData);
      }
    }, ServiceHelpers.handleErrorIn($q, $log, path));
  };

  /**
   * Converts the given deserialized JSON into a set of (tournament ID/pair number) pairs.
   * @param {*} data The JSON data received from the server.
   * @private
   * @returns {{tournamentId: string, pairNo: number}[]}
   */
  TichuCodeService.prototype._parseCodeResponse = function _parseCodeResponse(data) {
    ServiceHelpers.assertType("code response", data, "object");
    var tournamentInfos = ServiceHelpers.assertType("tournament infos", data["tournament_infos"], "array");
    return tournamentInfos.map(function(tournamentInfo, index) {
      var context = "tournament info[" + index + "]";
      ServiceHelpers.assertType(context + " tournament ID", tournamentInfo["tournament_id"], "string");
      ServiceHelpers.assertType(context + " pair number", tournamentInfo["pair_no"], "number");
      return {
        tournamentId: tournamentInfo["tournament_id"],
        pairNo: tournamentInfo["pair_no"]
      };
    });
  };

  angular.module("tichu-code-service", ["ng"])
      .service("TichuCodeService", TichuCodeService);
})(angular);