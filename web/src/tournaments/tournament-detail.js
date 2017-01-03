"use strict";
(function(angular) {
  /**
   * Main controller for the tournament detail page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {$mdDialog} $mdDialog
   * @param {angular.$window} $window
   * @param {angular.$location} $location
   * @param {$route} $route
   * @param {{failure: {redirectToLogin: boolean, error: string, detail: string}, tournament: Tournament}} loadResults
   * @ngInject
   */
  function TournamentDetailController($scope, $mdDialog, $window, $location, $route, loadResults) {
    $scope.appController.setPageHeader({
      header: loadResults.failure ? "Tournament Error" : loadResults.tournament.name,
      backPath: "/tournaments",
      showHeader: true
    });


    /**
     * The tournament being displayed to the user.
     *
     * @type {!tichu.Tournament}
     * @export
     */
    this.tournament = loadResults.tournament;

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
      $mdDialog.show(dialog).then(function () {
        if (redirectToLogin) {
          // use $window.location since we're going out of the Angular app
          $window.location.href = '/api/login?then=' + encodeURIComponent($location.url())
        } else {
          $route.reload();
        }
      }, function (autoHidden) {
        if (!autoHidden) {
          $location.url("/home");
        }
      });

      $scope.$on("$destroy", function () {
        $mdDialog.cancel(true);
      });
    }
  }

  /**
   * Asynchronously loads the requested tournament.
   *
   * @param {TichuTournamentService} tournamentService
   * @param {string} id
   * @return {!angular.$q.Promise}
   */
  function loadTournament(tournamentService, id) {
    return tournamentService.getTournament(id).then(function(result) {
      return {
        tournament: result
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
        .when("/tournaments/:id", {
          templateUrl: "src/tournaments/tournament-detail.html",
          controller: "TournamentDetailController",
          controllerAs: "tournamentDetailController",
          resolve: {
            "loadResults": /** @ngInject */ function($route, TichuTournamentService) {
              return loadTournament(TichuTournamentService, $route.current.params["id"]);
            }
          }
        });
  }

  angular.module("tichu-tournament-detail", ["ng", "ngRoute", "ngMaterial", "tichu-tournament-service"])
      .controller("TournamentDetailController", TournamentDetailController)
      .config(mapRoute);
})(angular);