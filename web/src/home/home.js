"use strict";
(function(angular) {
  /**
   * Main controller for the tournament list page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {!angular.$location} $location
   * @ngInject
   */
  function HomeController($scope, $location) {
    $scope.appController.setPageHeader({
      showHeader: false
    });

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

    /**
     * The injected location service.
     * @type {angular.$location}
     */
    this.$location = $location;
  }

  HomeController.prototype.loadCode = function loadCode() {
    this.loading = true;
    this.$location
        .path("/tournaments/which-generated-" + this.code.toUpperCase() + "/movement/1")
        .search({playerCode: this.code.toUpperCase()});
  };

  /**
   * Configures the routing provider to load the home screen at its path.
   *
   * @param {!$routeProvider} $routeProvider
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

  angular.module("tichu-home", ["ng", "ngRoute", "ngMaterial"])
      .controller("HomeController", HomeController)
      .config(mapRoute);
})(angular);