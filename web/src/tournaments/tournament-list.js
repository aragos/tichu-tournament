"use strict";
(function(angular) {
  /**
   * Main controller for the tournament list page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {!angular.$window} $window
   * @param {!$route} $route
   * @param {!angular.$location} $location
   * @param {!$mdDialog} $mdDialog
   * @param {!{failure: {redirectToLogin: boolean, error: string, detail: string}, tournaments: !tichu.TournamentHeader[]}} loadResults
   * @ngInject
   */
  function TournamentListController($scope, $window, $route, $location, $mdDialog, loadResults) {
    $scope.appController.setPageHeader({
      header: "Tournaments",
      backPath: "/home",
      showHeader: true
    });

    /**
     * List of tournaments to be displayed to the user.
     *
     * @type {!tichu.TournamentHeader[]}
     * @export
     */
    this.tournaments = loadResults.tournaments;

    /**
     * The details about the failure, if there was one.
     *
     * @type {{redirectToLogin: boolean, error: string, detail: string}}
     */
    this.failure = loadResults.failure;

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
      $mdDialog.show(dialog).then(function() {
        if (redirectToLogin) {
          // use $window.location since we're going out of the Angular app
          $window.location.href = '/api/login?then=' + encodeURIComponent($location.url())
        } else {
          $route.reload();
        }
      }, function(autoHidden) {
        if (!autoHidden) {
          $location.url("/home");
        }
      });

      $scope.$on("$destroy", function() {
        $mdDialog.cancel(true);
      });
    }
  }

  /**
   * Asynchronously loads the list of tournaments.
   *
   * @param {TichuTournamentService} tournamentService
   * @return {!angular.$q.Promise}
   */
  function loadTournamentList(tournamentService) {
    return tournamentService.getTournaments().then(function(result) {
      return {
        tournaments: result
      };
    }).catch(function(rejection) {
      return {
        failure: rejection
      };
    });
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
            "loadResults": /** @ngInject */ function(TichuTournamentService) {
              return loadTournamentList(TichuTournamentService);
            }
          }
        });
  }

  angular.module("tichu-tournament-list", ["ng", "ngRoute", "ngMaterial", "tichu-tournament-service"])
      .controller("TournamentListController", TournamentListController)
      .config(mapRoute);
})(angular);