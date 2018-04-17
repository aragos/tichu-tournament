"use strict";
(function(angular) {
  /**
   * Main controller for the tournament list page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {$mdDialog} $mdDialog
   * @param {$mdToast} $mdToast
   * @param {TichuMovementService} TichuMovementService
   * @param {angular.$q} $q
   * @param {$log} $log
   * @param {angular.$window} $window
   * @param {angular.$location} $location
   * @param {$route} $route
   * @param {!{pairCode: ?string, failure: (tichu.RpcError|undefined), movement: (tichu.Movement|undefined)}} loadResults
   * @ngInject
   */
  function MovementDetailController($scope, $mdDialog, $mdToast, TichuMovementService, $q, $log, $window, $location, $route, loadResults) {
    $scope.appController.setPageHeader({
      header: loadResults.failure
          ? "Movement Error"
          : "Pair #" + loadResults.movement.pair.pairNo + " - " + loadResults.movement.tournamentId.name,
      backPath: (loadResults.pairCode || loadResults.failure) ? "/home" : "/tournaments/" + loadResults.movement.tournamentId.id + "/view",
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
     * The movement being displayed.
     * @type {tichu.Movement}
     * @export
     */
    this.movement = loadResults.movement;

    /**
     * The player code which was used, if any.
     *
     * @type {?string}
     * @export
     */
    this.playerCode = loadResults.pairCode;

    /**
     * The error experienced while loading, if any.
     * @type {tichu.RpcError}
     * @export
     */
    this.failure = loadResults.failure;

    /**
     * The dialog service injected at creation.
     * @type {$mdDialog}
     * @private
     */
    this._$mdDialog = $mdDialog;

    /**
     * The toast service injected at creation.
     * @type {$mdToast}
     * @private
     */
    this._$mdToast = $mdToast;

    /**
     * The promise service injected at creation.
     * @type {angular.$q}
     * @private
     */
    this._$q = $q;

    /**
     * The logging service injected at creation.
     * @type {$log}
     * @private
     */
    this._$log = $log;

    /**
     * Whether a dialog is currently visible.
     * @type {boolean}
     * @private
     */
    this._showingDialog = false;

    /**
     * The movement service used to refresh the movement.
     * @type {TichuMovementService}
     * @private
     */
    this._movementService = TichuMovementService;

    /**
     * Whether this page has already exited.
     * @type {boolean}
     * @private
     */
    this._destroyed = false;

    var self = this;
    if (this.failure) {
      var hasPlayerCode = !!this.playerCode;
      var redirectToLogin = this.failure.redirectToLogin;
      var dialog = $mdDialog.confirm()
          .title(this.failure.error)
          .textContent(this.failure.detail);
      if (redirectToLogin) {
        if (hasPlayerCode) {
          dialog = dialog
              .ok("Try a different code")
              .cancel("Never mind")
        } else {
          dialog = dialog
              .ok("Log me in")
              .cancel("Never mind");
        }
      } else {
        dialog = dialog
            .ok("Try again")
            .cancel("Never mind");
      }
      $mdDialog.show(dialog).then(function () {
        if (redirectToLogin && hasPlayerCode) {
          $location.url("/home");
        } else if (redirectToLogin && !hasPlayerCode) {
          // use $window.location since we're going out of the Angular app
          $window.location.href = '/api/login?then=' + encodeURIComponent($location.url())
        } else {
          $route.reload();
        }
      }, function (autoHidden) {
        if (!autoHidden) {
          $location.url("/home");
        }
      }).finally(function () {
        self._showingDialog = false;
      });
      $scope.$on("$destroy", function () {
        self._destroyed = true;
        $mdDialog.cancel(true);
      });
    } else {
      $scope.$on("$destroy", function () {
        self._destroyed = true;
      });
    }
  }

  /**
   * Launches a dialog to edit the given hand.
   * @param {tichu.MovementRound} round
   * @param {tichu.Hand} hand
   */
  MovementDetailController.prototype.editHand = function editHand(round, hand) {
    if (this._showingDialog) {
      return;
    }
    this._showingDialog = true;
    var $mdDialog = this._$mdDialog;
    var self = this;
    var $q = this._$q;
    $mdDialog.show({
      controller: 'ScoreDetailController',
      controllerAs: 'scoreDetailController',
      templateUrl: 'src/movements/score-detail.html',
      locals: {
        loadResults: {
          hand: hand,
          pairCode: this.playerCode,
          position: round.position,
          tournamentId: this.movement.tournamentId.id
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
  };

  /**
   * Updates the movement with the latest data from the server.
   */
  MovementDetailController.prototype._refresh = function refresh() {
    var $mdToast = this._$mdToast;
    var $q = this._$q;
    var self = this;
    return this._movementService.getMovement(
        this.movement.tournamentId.id, this.movement.pair.pairNo, this.playerCode, true).then(function() {
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
   * Formats the given call into a string.
   * @param {{side: tichu.Position, call: tichu.Call}} call
   * @returns {?string}
   */
  function formatCall(call) {
    if (!call) {
      return null;
    }
    return call.side[0].toUpperCase() + "(" + call.call + ")";
  }

  /**
   * Asynchronously loads the movement specified by the tournament and pair.
   *
   * @param {TichuMovementService} movementService
   * @param {string} tournamentId
   * @param {number} pairNo
   * @param {?string=} playerCode
   * @returns {angular.$q.Promise<{pairCode: ?string, failure: (tichu.RpcError|undefined), movement: (tichu.Movement|undefined)}>}
   */
  function loadMovement(movementService, tournamentId, pairNo, playerCode) {
    return movementService.getMovement(tournamentId, pairNo, playerCode).then(function(movement) {
      return {
        pairCode: playerCode,
        movement: movement
      };
    }).catch(function(failure) {
      return {
        pairCode: playerCode,
        failure: failure
      }
    });
  }


  /**
   * Configures the routing provider to load the movement detail page at its path.
   *
   * @param {$routeProvider} $routeProvider
   * @ngInject
   */
  function mapRoute($routeProvider) {
    $routeProvider
        .when("/tournaments/:tournamentId/movement/:pairNo", {
          templateUrl: "src/movements/movement-detail.html",
          controller: "MovementDetailController",
          controllerAs: "movementDetailController",
          resolve: {
            "loadResults": /** @ngInject */ function(TichuMovementService, $route) {
              return loadMovement(
                  TichuMovementService,
                  $route.current.params["tournamentId"],
                  parseInt($route.current.params["pairNo"]),
                  $route.current.params["playerCode"] || null);
            }
          }
        });
  }

  angular.module("tichu-movement-detail",
          ["ng", "ngRoute", "ngMaterial", "tichu-movement-service", "tichu-score-detail"])
      .controller("MovementDetailController", MovementDetailController)
      .config(mapRoute)
      .filter("tichuMovementFormatCall", function() {
        return formatCall;
      });
})(angular);