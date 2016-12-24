"use strict";
(function(angular) {
  /**
   * Main controller for the tournament list page.
   *
   * @constructor
   * @param {angular.Scope} $scope
   * @param {{tournamentId: string, pairNo: number, pairId: (string|undefined), movement: !tichu.Movement}} movementData
   * @ngInject
   */
  function MovementDetailController($scope, movementData) {
    $scope.appController.showHeader = true;
    $scope.appController.header = "Pair #" + movementData.pairNo + " - " + movementData.movement["name"];

    /**
     * The ID of the tournament this movement is from.
     *
     * @type {string}
     * @export
     */
    this.tournamentId = movementData.tournamentId;

    /**
     * The number of the pair whose movement is being displayed.
     *
     * @type {number}
     * @export
     */
    this.pairNo = movementData.pairNo;

    /**
     * Whether a pair ID was used.
     *
     * @type {boolean}
     * @export
     */
    this.usedPairId = !!movementData.pairId;

    /**
     * The full movement information.
     *
     * @type {!tichu.Movement}
     * @export
     */
    this.movement = movementData.movement;
  }

  /**
   * Asynchronously loads the movement.
   *
   * @param {angular.$q} $q
   * @param {string} tournamentId
   * @param {number} pairNo
   * @param {string} pairId
   * @returns {angular.$q.Promise<{tournamentId: string, pairNo: number, pairId: (string|undefined), movement: !tichu.Movement}>}
   */
  function loadMovement($q, tournamentId, pairNo, pairId) {
    return $q.when({
      tournamentId: tournamentId,
      pairNo: pairNo,
      pairId: pairId,
      movement: {
          name: "Tournament " + tournamentId,
          players: [{
            name: "Player " + pairNo + ".1" + pairId,
            email: "first" + pairNo + "@email.com"
          }, {
            name: "Player " + pairNo + ".2" + pairId,
            email: "second" + pairNo + "@email.com"
          }],
          "movement": [{
            "round": 1,
            "position": "3N",
            "opponent": 2,
            "hands": [3, 4, 5],
            "relay_table": 5,
            "score" : {
              "calls": {
                "north": "T",
                "east": "GT",
                "west": "",
                "south": ""
              },
              "ns_score": 150,
              "ew_score": -150,
              "notes": "I am a note"
            }},
            {
              "round": 2,
              "position": "1E",
              "opponent": 4,
              "hands": [7, 8, 9]
            }]
        }
    });
  }

  /**
   * Configures the routing provider to load the tournament list at /tournaments.
   *
   * @param {$routeProvider} $routeProvider
   * @ngInject
   */
  function mapRoute($routeProvider) {
    $routeProvider
        .when("/tournaments/:tournamentId/movement/:pairNo", {
          templateUrl: "src/movements/movement-detail.html",
          controller: "MovementDetailController",
          controllerAs: "movementDetailController",
          resolve: {
            "movementData": /** @ngInject */ function($q, $route) {
              return loadMovement(
                  $q,
                  $route.current.params["tournamentId"],
                  parseInt($route.current.params["pairNo"]),
                  $route.current.params["pairId"]);
            }
          }
        });
  }

  angular.module("tichu-movement-detail", ["ng", "ngRoute"])
      .controller("MovementDetailController", MovementDetailController)
      .config(mapRoute);
})(angular);