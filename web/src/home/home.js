"use strict";
(function(angular) {
  /**
   * Main controller for the home page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {!angular.$location} $location
   * @param {!$mdDialog} $mdDialog
   * @param {!TichuCodeService} TichuCodeService
   * @ngInject
   */
  function HomeController($scope, $location, $mdDialog, TichuCodeService) {
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
     * The code the user has currently entered.
     *
     * @export
     * @type {string}
     */
    this.code = "";

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

    this._codeService.getMovementForCode(code).then(function(result) {
      self._$location
          .path("/tournaments/" + encodeURIComponent(result.tournamentId)
              + "/movement/" + encodeURIComponent(result.pairNo.toString()))
          .search({playerCode: code.toUpperCase()});
    }).catch(function(failure) {
      self.loading = false;
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

  angular.module("tichu-home", ["ng", "ngRoute", "ngMaterial", "tichu-code-service"])
      .controller("HomeController", HomeController)
      .config(mapRoute);
})(angular);