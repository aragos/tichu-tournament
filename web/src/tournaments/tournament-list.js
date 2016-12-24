"use strict";
(function(angular) {
  /**
   * Main controller for the tournament list page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {!tichu.TournamentSummary[]} tournaments
   * @ngInject
   */
  function TournamentListController($scope, tournaments) {
    $scope.appController.setPageHeader({
      header: "Tournaments",
      backPath: "/home",
      showHeader: true
    });

    /**
     * List of tournaments to be displayed to the user.
     *
     * @type {!tichu.TournamentSummary[]}
     * @export
     */
    this.tournaments = tournaments;
  }

  /**
   * Asynchronously loads the list of tournaments.
   *
   * @param {!angular.$q} $q
   * @return {!angular.$q.Promise<tichu.TournamentSummary>}
   */
  function loadTournamentList($q) {
    return $q.when([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17].map(function(index) {
      return {"id": (37 * index).toString(), "name": "Example Tournament #" + index};
    }));
  }

  /**
   * Configures the routing provider to load the tournament list at its path.
   *
   * @param {!$routeProvider} $routeProvider
   * @ngInject
   */
  function mapRoute($routeProvider) {
    $routeProvider
        .when("/tournaments", {
          templateUrl: "src/tournaments/tournament-list.html",
          controller: "TournamentListController",
          controllerAs: "tournamentListController",
          resolve: {
            "tournaments": /** @ngInject */ function($q) {
              return loadTournamentList($q);
            }
          }
        });
  }

  angular.module("tichu-tournament-list", ["ng", "ngRoute"])
      .controller("TournamentListController", TournamentListController)
      .config(mapRoute);
})(angular);