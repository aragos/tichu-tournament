"use strict";
(function(angular) {
  /**
   * Main app controller for the tichu-tournament app.
   *
   * @constructor
   * @ngInject
   */
  function AppController() {
    /**
     * The current header (displayed in the toolbar).
     *
     * @export
     * @type {string}
     */
    this.header = "Tichu Tournament";

    /**
     * The current page title. Appended to the header and displayed as the <title>.
     *
     * @export
     * @type {string}
     */
    this.title = "Tichu Tournament";
  }

  /**
   * Sets up the Angular Material theme.
   *
   * @param {md.$mdThemingProvider} $mdThemingProvider
   * @ngInject
   */
  function configureTheme($mdThemingProvider){
    $mdThemingProvider.theme('default')
        .primaryPalette('red')
        .accentPalette('blue');
  }

  /**
   * Configures the routing provider to go to /tournaments when no other page is specified.
   * (e.g., on initial load)
   *
   * @param {angular.$routeProvider} $routeProvider
   * @ngInject
   */
  function setDefaultRoute($routeProvider) {
    $routeProvider
        .otherwise("/tournaments");
  }

  angular.module("tichu-tournament", ["ng", "ngRoute", "ngMaterial", "tichu-tournament-list"])
      .controller("AppController", AppController)
      .config(configureTheme)
      .config(setDefaultRoute);
})(angular);