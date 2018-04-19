"use strict";
(function(angular) {
  /**
   * Main controller for the home page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {!angular.$location} $location
   * @param {!$mdDialog} $mdDialog
   * @param {!$cookies} $cookies
   * @param {!TichuCodeService} TichuCodeService
   * @ngInject
   */
  function HomeController($scope, $location, $mdDialog, $cookies, TichuCodeService) {
    $scope.appController.setPageHeader({
      showHeader: false
    });

    /**
     * The scope this controller is functioning in.
     * @type {!angular.Scope}
     * @private
     */
    this._$scope = $scope;

    /**
     * The dialog service used to alert on errors.
     * @type {$mdDialog}
     * @private
     */
    this._$mdDialog = $mdDialog;

    /**
     * The cookie service used to persist the code.
     * @type {$cookies}
     * @private
     */
    this._$cookies = $cookies;

     /**
     * The code the user has currently entered.
     *
     * @export
     * @type {string}
     */
    this.code = "";
    if (this._$cookies.get("playerCode") != "") {
      this.code = this._$cookies.get("playerCode");
    }

    /**
     * The code service used to request the movement information from the server.
     *
     * @type {TichuCodeService}
     * @private
     */
    this._codeService = TichuCodeService;

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
     * @private
     */
    this._$location = $location;
  }

  /**
   * Loads the movement data based on the code in the scope.
   */
  HomeController.prototype.loadCode = function loadCode() {
    if (this.loading) {
      return;
    }
    this.code = this.code.toUpperCase();
    this.loading = true;
    var code = this.code;
    var self = this;

    self._$cookies.put("playerCode", code);

    this._codeService.getMovementForCode(code).then(function(result) {
      self._$location
          .path("/tournaments/" + encodeURIComponent(result.tournamentId)
              + "/movement/" + encodeURIComponent(result.pairNo.toString()))
          .search({playerCode: code.toUpperCase()});
    }).catch(function(failure) {
      self.loading = false;
      self._$cookies.put("playerCode", "");
      var alert = self._$mdDialog.alert()
          .title(failure.error)
          .textContent(failure.detail)
          .ok("Try again");
      var dialogDestroyed = false;
      self._$mdDialog.show(alert).then(function() {
        dialogDestroyed = true;
      });
      self._$scope.$on("$destroy", function() {
        if (!dialogDestroyed) {
          self._$mdDialog.hide();
        }
      });
    });
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

  angular.module("tichu-home", ["ng", "ngRoute", "ngMaterial", "ngCookies", "tichu-code-service"])
      .controller("HomeController", HomeController)
      .config(mapRoute);
})(angular);
