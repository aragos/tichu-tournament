"use strict";
(function(angular) {
  /**
   * Main controller for the tournament edit page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {$mdToast} $mdToast
   * @param {TichuTournamentService} TichuTournamentService
   * @param {$mdDialog} $mdDialog
   * @param {angular.$window} $window
   * @param {angular.$location} $location
   * @param {$route} $route
   * @param {!{failure: ?tichu.RpcError, id: ?string, tournamentStatus: ?tichu.TournamentStatus}} loadResults
   * @ngInject
   */
  function TournamentStatusController($scope, $mdToast, TichuTournamentService, $mdDialog, $log, $window, $location, $route, loadResults) {
    var backPath = "/tournaments" + (loadResults.id ? "/" + loadResults.id + "/view" : "");
    $scope.appController.setPageHeader({
      header: loadResults.failure
          ? "Tournament Error"
          : (loadResults.tournament ? "Editing " + loadResults.id : "Tournament Status"),
      backPath: backPath,
      showHeader: true,
      refresh: loadResults.failure ? null : this._refresh.bind(this)
    });

    $scope.$on('$locationChangeStart', 
      function(event) {
        if (angular.element(document.body).hasClass('md-dialog-is-showing')) {
          event.preventDefault();
          $mdDialog.cancel();
       }
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
     * The tournament id of the tournament we're looking up.
     *
     * @type {string}
     */
    this.tournamentId = loadResults.id;
    
    /**
     * The status of all hands in the tournament.
     *
     * @type {tichu.TournamentStatus}
     */
    this.tournamentStatus = loadResults.tournamentStatus

    /**
     * Whether to show scored hands in the expander list or not. 
     *
     * @type {boolean[]}
     */
    this.showScored = []
    
    /**
     * Whether to show unscored hands in the expander list or not. 
     *
     * @type {boolean[]}
     */
    this.showUnscored = []

    /**
     * The logging service injected at creation.
     * @type {$log}
     * @private
     */
    this._$log = $log;

    /** The location service injected at creation. */
    this._$location = $location;

    /** The scope this controller exists in. */
    this._$scope = $scope;
    
    /**
     * Whether a dialog is currently visible.
     * @type {boolean}
     * @private
     */
    this._showingDialog = false;

    /**
     * The toast service injected at creation.
     * @type {$mdToast}
     * @private
     */
    this._$mdToast = $mdToast;

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
   * Launches a dialog to edit the given hand.
   * @param {number} hand_no Hand number of the hand to edit.
   * @param {number} ns_pair Pair sitting in the North/South position for this hand.
   * @param {number} ew_pair Pair sitting in the East/West position for this hand.
   */
  TournamentStatusController.prototype.editHand = function editHand(hand_no, ns_pair, ew_pair) {
    if (this._showingDialog) {
      return;
    }
    this._showingDialog = true;
    var $mdDialog = this._$mdDialog;
    var self = this;
    var $q = this._$q;
    var $log = this._$log;
    var tournamentId = this.tournamentId;
    this._tournamentService.getHand(tournamentId, hand_no, ns_pair, ew_pair)
    .then(function(this_hand) {
      $mdDialog.show({
        controller: 'ScoreDetailController',
        controllerAs: 'scoreDetailController',
        templateUrl: 'src/movements/score-detail.html',
        locals: {
          loadResults: {
            hand: this_hand,
            tournamentId: tournamentId
          }
        },
        clickOutsideToClose: false,
        escapeToClose: false,
        fullscreen: true
      }).catch(function(rejection) {
        if (!rejection) {
          /* The dialog was canceled or auto-hidden. That's okay. */
          return;
        }
        $log.error("Something went wrong while showing the score detail: " + rejection);
      }).finally(function() {
        self._showingDialog = false;
      })
    }).catch(function(/** tichu.RpcError */ error) {
      return $q.reject(error);
    });
  };

  /**
   * Updates the status with the latest data from the server.
   */
  TournamentStatusController.prototype._refresh = function refresh() {
    var $mdToast = this._$mdToast;
    var $q = this._$q;
    var self = this;
    return this._tournamentService.getTournamentStatus(
        this.tournamentId).then(function() {
      if (!self._destroyed) {
        $mdToast.showSimple("Refreshed!");
      }
    }).catch(function(/** tichu.RpcError */ error) {
      if (!self._destroyed) {
        $mdToast.showSimple("Failed to refresh: " + error.error);
      }
      return $q.reject(error);
    });
  };

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