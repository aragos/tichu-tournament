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
     * The current header (displayed in the toolbar and page title), or null to hide header text.
     *
     * @export
     * @type {?string}
     */
    this.header = "Tichu Tournament";

    /**
     * The path the back button should go to, or null to hide the back button.
     *
     * @export
     * @type {?string}
     */
    this.backPath = "/home";

    /**
     * Whether the toolbar should be displayed.
     *
     * @export
     * @type {boolean}
     */
    this.showHeader = true;

    /**
     * The current page title. Appended to the header and displayed as the <title>.
     *
     * @export
     * @type {string}
     */
    this.title = "Tichu Tournament";
  }

  /**
   * Configures the header for this page.
   *
   * @param {!{header: (?string|undefined), backPath: (?string|undefined), showHeader: (?boolean|undefined)}} options
   *     The options dictionary.
   *     header: The page header; is cleared (no page header text) if the options header is null or unset.
   *     backPath: The back button path; is cleared (no back button) if the options path is null or unset.
   *     showHeader: Whether to show the toolbar; defaults to true if null or unset. Only has any effect
   *         if the header or backPath are set.
   */
  AppController.prototype.setPageHeader = function setPageHeader(options) {
    this.header = options.header || null;
    this.backPath = options.backPath || null;
    this.showHeader = options.showHeader !== false;
  };

  /**
   * Sets up the Angular Material theme.
   *
   * @param {!$mdThemingProvider} $mdThemingProvider
   * @ngInject
   */
  function configureTheme($mdThemingProvider){
    $mdThemingProvider.theme('default')
        .primaryPalette('red')
        .accentPalette('blue');
  }

  /**
   * Configures the routing provider to go to /home when no other page is specified.
   * (e.g., on initial load) Also configures html5mode.
   *
   * @param {!$locationProvider} $locationProvider
   * @param {!$routeProvider} $routeProvider
   * @ngInject
   */
  function setDefaultRoute($locationProvider, $routeProvider) {
    $routeProvider
        .otherwise("/home");
    $locationProvider.html5Mode({
      enabled: true,
      requireBase: true,
      rewriteLinks: true
    })
  }

  angular.module("tichu-tournament", [
          "ng",
          "ngRoute",
          "ngMaterial",
          "ngMessages",
          "tichu-home",
          "tichu-movement-detail",
          "tichu-tournament-detail",
          "tichu-tournament-list",
          "tichu-tournament-service"])
      .controller("AppController", AppController)
      .config(configureTheme)
      .config(setDefaultRoute);
})(angular);