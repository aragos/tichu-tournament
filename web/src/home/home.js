"use strict";
(function(angular) {
  /**
   * Main controller for the tournament list page.
   *
   * @constructor
   * @param {angular.Scope} $scope
   * @ngInject
   */
  function HomeController($scope) {
    $scope.appController.showHeader = false;
    $scope.appController.header = "";

    /**
     * The code the user has currently entered.
     *
     * @export
     * @type {string}
     */
    this.code = "";

    /**
     * Whether the user has entered a code and clicked to load their hands.
     *
     * @export
     * @type {boolean}
     */
    this.loading = false;
  }

  HomeController.prototype.loadCode = function loadCode() {
    this.loading = true;
  };

  /**
   * Configures the routing provider to load the tournament list at /tournaments.
   *
   * @param {$routeProvider} $routeProvider
   * @ngInject
   */
  function mapRoute($routeProvider) {
    $routeProvider
        .when("/home", {
          templateUrl: "src/home/home.html",
          controller: "HomeController",
          controllerAs: "homeController"
        });
  }

  angular.module("tichu-home", ["ng", "ngRoute"])
      .controller("HomeController", HomeController)
      .config(mapRoute);
})(angular);