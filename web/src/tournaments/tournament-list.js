"use strict";
(function(angular) {
  /**
   * Main controller for the tournament list page.
   *
   * @constructor
   * @param {$log} $log
   * @param {!angular.Scope} $scope
   * @param {!angular.$window} $window
   * @param {!$route} $route
   * @param {!angular.$location} $location
   * @param {!$mdDialog} $mdDialog
   * @param {!{failure: ?tichu.RpcError, tournaments: ?tichu.TournamentHeader[]}} loadResults
   * @ngInject
   */
  function TournamentListController($log, $scope, $window, $route, $location, $mdDialog, TichuTournamentService, loadResults) {
    $scope.appController.setPageHeader({
      header: "Tournaments",
      backPath: "/home",
      showHeader: true
    });

    /**
     * The dialog service injected at creation.
     * @type {$mdDialog}
     * @private
     */
    this._$mdDialog = $mdDialog;

    /**
     * The routing service injected at creation.
     * @type {$route}
     * @private
     */
    this._$route = $route;

    /**
     * The logging service injected at creation.
     * @type {$log}
     * @private
     */
    this._$log = $log;

    /**
     * The tournament service injected at creation.
     * @type {TichuTournamentService}
     * @private
     */
    this._tournamentService = TichuTournamentService;

    /**
     * List of tournaments to be displayed to the user.
     *
     * @type {?tichu.TournamentHeader[]}
     * @export
     */
    this.tournaments = loadResults.tournaments;

    /**
     * The details about the failure, if there was one.
     *
     * @type {?tichu.RpcError}
     */
    this.failure = loadResults.failure;

    if (this.failure) {
      var redirectToLogin = this.failure.redirectToLogin;
      var dialog = this._$mdDialog.confirm()
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
      this._$mdDialog.show(dialog).then(function() {
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
        this._$mdDialog.cancel(true);
      });
    }
  }

  /** 
   * Deletes the selected tournament.
   */
  TournamentListController.prototype.deleteTournament = function deleteTournament(id, tournamentName) {
    var dialog = this._$mdDialog.confirm()
          .title("Confirm Deletion")
          .textContent("Permanently delete \"" + tournamentName + "\"?")
          .ok("CONFIRM")
          .cancel("CANCEL");
    $log = this._$log;
    $route = this._$route;
    self = this;
    tournamentService = this._tournamentService;
    this._$mdDialog.show(dialog).then(function(){
      tournamentService.deleteTournament(id).then(function(results) {
        self.tournaments = results;
      }, function(rejection) {
        $log.error("Something went wrong while deleting the tournament: " + rejection);
        $route.reload();
      });
    }).catch(function(rejection) {
      if (!rejection) {
        /* The dialog was canceled or auto-hidden. That's okay. */
        return;
      }
      $log.error("Something went wrong while deleting the tournament: " + rejection);
    });
  }

  /**
   * Asynchronously loads the list of tournaments.
   *
   * @param {TichuTournamentService} tournamentService
   * @return {!angular.$q.Promise<!{failure: ?tichu.RpcError, tournaments: ?tichu.TournamentHeader[]}>}
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