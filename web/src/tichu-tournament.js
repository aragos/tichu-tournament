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
     * The function which causes the current page to refresh.
     *
     * @export
     * @type {?function():angular.$q.Promise}
     */
    this.refresher = null;

    /**
     * Whether the most recent refresh succeeded, or null to indicate that a refresh is in progress.
     *
     * @export
     * @type {?boolean}
     */
    this.refreshStatus = true;

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
   * @param {!{header: ?string=, backPath: ?string=, showHeader: ?boolean=, refresh: ?function():angular.$q.Promise=}} options
   *     The options dictionary.
   *     header: The page header; is cleared (no page header text) if the options header is null or unset.
   *     backPath: The back button path; is cleared (no back button) if the options path is null or unset.
   *     showHeader: Whether to show the toolbar; defaults to true if null or unset. Only has any effect
   *         if the header or backPath are set.
   *     refresh: A function to call when the back button is pressed.
   */
  AppController.prototype.setPageHeader = function setPageHeader(options) {
    this.header = options.header || null;
    this.backPath = options.backPath || null;
    this.showHeader = options.showHeader !== false;
    this.refreshStatus = true;
    this.refresher = options.refresh || null;
  };

  /**
   * Runs the refresh, toggling the status of the refresh variable appropriately.
   */
  AppController.prototype.refresh = function refresh() {
    if (!this.refresher) {
      return;
    }
    this.refreshStatus = null;
    var self = this;
    this.refresher.call(null).then(function() {
      self.refreshStatus = true;
    }).catch(function() {
      self.refreshStatus = false;
    });
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
   * The regexp used to match old-style tournament URLs in otherwise.
   * @const {RegExp}
   */
  var OLD_STYLE_TOURNAMENT_URL = /^\/tournaments\/([^/]+)(?:\/)?$/;

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
        .otherwise({
          redirectTo: function(routeParams, path) {
            var match = OLD_STYLE_TOURNAMENT_URL.exec(path);
            if (match) {
              return "/tournaments/" + match[1] + "/view"
            }
            return "/home";
          }
        });
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
          "tichu-tournament-form",
          "tichu-tournament-list",
          "tichu-tournament-results"])
      .controller("AppController", AppController)
      .config(configureTheme)
      .config(setDefaultRoute);
})(angular);