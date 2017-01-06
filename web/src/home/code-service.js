"use strict";
(function(angular) {
  /**
   * Service to interact with the server's player code translation API.
   *
   * @constructor
   * @name TichuCodeService
   * @param {angular.$http} $http
   * @param {angular.$q} $q
   * @ngInject
   */
  function TichuCodeService($http, $q) {
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
  }

  /**
   * Makes a request for the tournament ID and pair number specified by the pair code.
   *
   * @param {string} pairCode The pair code to translate into tournament ID and pair number.
   * @returns {angular.$q.Promise<{tournamentId: string, pairNo: number}>}
   */
  TichuCodeService.prototype.getMovementForCode = function getMovementForCode(pairCode) {
    var $q = this._$q;
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
          return $q.reject({
            redirectToLogin: false,
            error: "No tournament found!",
            detail: "Check the pair code the tournament director gave you and try again."
          });
        } else {
          return $q.reject({
            redirectToLogin: false,
            error: "Bad luck!",
            detail: "What are the odds?! There are multiple tournaments that your pair code could be for..."
          });
        }
      } catch (ex) {
        console.log(
            "Malformed response from " + path + " (" + response.status + " " + response.statusText + "):\n"
            + ex + "\n\n"
            + JSON.stringify(response.data));
        return $q.reject({
          redirectToLogin: false,
          error: "Invalid response from server",
          detail: "The pair information... wasn't."
        });
      }
    }, ServiceHelpers.handleErrorIn($q, path));
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