"use strict";
(function(angular) {
  /**
   * Main controller for the tournament edit page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {TichuTournamentService} TichuTournamentService
   * @param {$mdDialog} $mdDialog
   * @param {angular.$window} $window
   * @param {angular.$location} $location
   * @param {$route} $route
   * @param {!{failure: ?tichu.RpcError, id: ?string, tournamentStatus: ?tichu.TournamentStatus}} loadResults
   * @ngInject
   */
  function TournamentStatusController($scope, TichuTournamentService, $mdDialog, $window, $location, $route, loadResults) {
    var backPath = "/tournaments" + (loadResults.id ? "/" + loadResults.id + "/view" : "");
    $scope.appController.setPageHeader({
      header: loadResults.failure
          ? "Tournament Error"
          : (loadResults.tournament ? "Editing " + loadResults.id : "Tournament Status"),
      backPath: backPath,
      showHeader: true
    });

    /**
     * The tournament service injected at creation.
     * @type {TichuTournamentService}
     * @private
     */
    this._tournamentService = TichuTournamentService;

    /**
     * The details about the failure, if there was one.
     *
     * @type {tichu.RpcError}
     */
    this.failure = loadResults.failure;
    
    /**
     * The status of all hands in the tournament.
     *
     * @type {tichu.TournamentStatus}
     */
    this.tournamentStatus = loadResults.tournamentStatus

    /** The location service injected at creation. */
    this._$location = $location;

    /** The scope this controller exists in. */
    this._$scope = $scope;

    /**
     * The dialog service injected at creation.
     * @type {$mdDialog}
     * @private
     */
    this._$mdDialog = $mdDialog;

    if (this.failure) {
      var redirectToLogin = this.failure.redirectToLogin;
      var dialog = $mdDialog.confirm()
          .title(this.failure.error)
          .textContent(this.failure.detail);
      if (redirectToLogin) {
        dialog = dialog
            .ok("Log me in")
            .cancel("Never mind");
      } else {
        dialog = dialog
            .ok("Try again")
            .cancel("Never mind");
      }
      $mdDialog.show(dialog).then(function () {
        if (redirectToLogin) {
          // use $window.location since we're going out of the Angular app
          $window.location.href = '/api/login?then=' + encodeURIComponent($location.url())
        } else {
          $route.reload();
        }
      }, function (autoHidden) {
        if (!autoHidden) {
          $location.url(backPath);
        }
      });

      $scope.$on("$destroy", function () {
        $mdDialog.cancel(true);
      });
    }
  }

  /**
   * Asynchronously loads the requested tournament status.
   *
   * @param {TichuTournamentService} tournamentService
   * @param {string} id
   * @return {!angular.$q.Promise<!{failure: ?tichu.RpcError, id: ?string, tournamentStatus: ?tichu.TournamentStatus}>}
   */
  function loadTournamentStatus(tournamentService, id) {
    return tournamentService.getTournamentStatus(id).then(function(result) {
      return {
        id: id,
        tournamentStatus: result
      };
    }).catch(function(rejection) {
      return {
        id: id,
        failure: rejection
      };
    });
  }

  /**
   * Configures the routing provider to load the tournament status at its path.
   *
   * @param {!$routeProvider} $routeProvider
   * @ngInject
   */
  function mapRoute($routeProvider) {
    $routeProvider
        .when("/tournaments/:id/status", {
          templateUrl: "src/tournaments/tournament-status.html",
          controller: "TournamentStatusController",
          controllerAs: "tournamentStatusController",
          resolve: {
            "loadResults": /** @ngInject */ function($route, TichuTournamentService) {
              return loadTournamentStatus(TichuTournamentService, $route.current.params["id"]);
            }
          }
        });
  }

  angular.module("tichu-tournament-status", ["ng", "ngRoute", "ngMaterial", "tichu-tournament-service"])
      .controller("TournamentStatusController", TournamentStatusController)
      .config(mapRoute);
})(angular);