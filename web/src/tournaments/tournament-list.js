"use strict";
(function(angular) {
  /**
   * Main controller for the tournament list page.
   *
   * @constructor
   * @param {angular.Scope} $scope
   * @ngInject
   */
  function TournamentListController($scope) {
    $scope.appController.showHeader = true;
    $scope.appController.header = "Tournaments";

    /**
     * List of tournaments to be displayed to the user.
     *
     * @type {{id:String,name:String}[]}
     * @export
     */
    this.tournaments = [{"id": "1234567890abcdef", "name": "example tournament"}];
  }

  /**
   * Configures the routing provider to load the tournament list at /tournaments.
   *
   * @param {angular.$routeProvider} $routeProvider
   * @ngInject
   */
  function mapRoute($routeProvider) {
    $routeProvider
        .when("/tournaments", {
          templateUrl: "src/tournaments/tournament-list.html",
          controller: "TournamentListController",
          controllerAs: "tournamentListController"
        });
  }

  angular.module("tichu-tournament-list", ["ng", "ngRoute"])
      .controller("TournamentListController", TournamentListController)
      .config(mapRoute);
})(angular);