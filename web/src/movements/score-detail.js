"use strict";
(function(angular) {
  /**
   * Main controller for the tournament list page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {$mdDialog} $mdDialog
   * @param {$location} $location
   * @param {$window} $window
   * @param {TichuMovementService} TichuMovementService
   * @param {{pairCode: ?string, hand: !tichu.Hand, position: tichu.PairPosition, tournamentId: string}} loadResults
   * @ngInject
   */
  function ScoreDetailController($scope, $mdDialog, $location, $window, TichuMovementService, loadResults) {
    /**
     * The scope this controller is attached to.
     * @type {angular.Scope}
     * @private
     */
    this._$scope = $scope;

    /**
     * Whether a pair code was used.
     * @type {?string}
     * @export
     */
    this.pairCode = loadResults.pairCode;

    /**
     * The hand being displayed.
     * @type {!tichu.Hand}
     * @export
     */
    this.hand = loadResults.hand;

    /**
     * The position to be displayed.
     * @type {tichu.PairPosition}
     * @export
     */
    this.position = loadResults.position;

    /**
     * The tournament ID this dialog is editing a score from.
     * @type {string}
     * @private
     */
    this._tournamentId = loadResults.tournamentId;

    /**
     * The current edited form of the score.
     * @type {{northSouthScore: string, eastWestScore: string, calls: Object.<tichu.Position, tichu.Call>, notes: string}}
     * @export
     */
    this.score = convertScoreToEditable(this.hand.score);

    /**
     * Whether an existing score should be overwritten.
     * @type {boolean}
     * @export
     */
    this.overwriting = false;

    /**
     * Whether the user has elected to delete the score instead.
     * @type {boolean}
     * @export
     */
    this.deleting = false;

    /**
     * Whether a save or delete operation is in progress.
     * @type {boolean}
     * @export
     */
    this.saving = false;

    /**
     * The error resulting from the last save or delete operation.
     * @type {?tichu.RpcError}
     * @export
     */
    this.saveError = null;

    /**
     * The dialog service used to close the dialog.
     * @type {$mdDialog}
     * @private
     */
    this._$mdDialog = $mdDialog;

    /**
     * The location service used to navigate if needed.
     * @type {$location}
     * @private
     */
    this._$location = $location;

    /**
     * The window used to log in if needed.
     * @type {$window}
     * @private
     */
    this._$window = $window;

    /**
     * The movement serice injected at creation.
     * @type {TichuMovementService}
     * @private
     */
    this._movementService = TichuMovementService;
  }

  /**
   * Closes the dialog without saving.
   * @export
   */
  ScoreDetailController.prototype.cancel = function cancel() {
    if (this.saving) {
      return;
    }
    this._$mdDialog.cancel();
  };

  /**
   * Closes the dialog and saves the result.
   * @export
   */
  ScoreDetailController.prototype.save = function save() {
    if (this.saving || this.saveFailure || (this.hand.score && !this.deleting && !this.overwriting)) {
      return;
    }
    this.saving = true;
    var promise;
    if (this.deleting) {
      promise = this._movementService.clearScore(
          this._tournamentId,
          this.hand.northSouthPair,
          this.hand.eastWestPair,
          this.hand.handNo,
          this.pairCode);
    } else {
      promise = this._movementService.recordScore(
          this._tournamentId,
          this.hand.northSouthPair,
          this.hand.eastWestPair,
          this.hand.handNo,
          convertEditableToScore(this.score),
          this.pairCode);
    }
    var $mdDialog = this._$mdDialog;
    var self = this;
    promise.then(function() {
      $mdDialog.hide();
    }).catch(function(rejection) {
      self.saving = false;
      self.saveError = rejection;
    });
  };

  /**
   * Sends the browser back to the home page.
   */
  ScoreDetailController.prototype.goHome = function goHome() {
    if (!this.saveError) {
      return;
    }
    this._$mdDialog.cancel();
    this._$location.url("/home");
  };

  /**
   * Sends the browser to the login page.
   */
  ScoreDetailController.prototype.login = function login() {
    if (!this.saveError) {
      return;
    }
    this._$mdDialog.cancel();
    this._$window.location.href = "/api/login?then=" + encodeURIComponent(this._$location.url());
  };

  /**
   * Clears the failure state.
   */
  ScoreDetailController.prototype.tryAgain = function tryAgain() {
    if (!this.saveError) {
      return;
    }
    this.saveError = null;
  };

  /**
   * Converts the given score to an easily editable format.
   * @param {!tichu.HandScore} score
   * @returns {!{northSouthScore: number, eastWestScore: number, calls: Object<tichu.Position, tichu.Call>, notes: string}}
   */
  function convertScoreToEditable(score) {
    if (!score) {
      return {
        northSouthScore: "0",
        eastWestScore: "0",
        calls: {},
        notes: ""
      };
    }
    var convertedCalls = {};
    score.calls.forEach(function(call) {
      convertedCalls[call.side] = call.call;
    });
    return {
      northSouthScore: score.northSouthScore.toString(),
      eastWestScore: score.eastWestScore.toString(),
      calls: convertedCalls,
      notes: score.notes
    };
  }

  /**
   * Converts the editable score back into a HandScore.
   * @param {!{northSouthScore: string, eastWestScore: string, calls: Object<tichu.Position, tichu.Call>, notes: string}} editable
   * @returns {!tichu.HandScore}
   */
  function convertEditableToScore(editable) {
    var score = new tichu.HandScore();
    var parsedNorthSouthScore = parseInt(editable.northSouthScore);
    var parsedEastWestScore = parseInt(editable.eastWestScore);
    score.northSouthScore = Number.isNaN(parsedNorthSouthScore) ? editable.northSouthScore : parsedNorthSouthScore;
    score.eastWestScore = Number.isNaN(parsedEastWestScore) ? editable.eastWestScore : parsedEastWestScore;
    score.notes = editable.notes;
    Object.keys(tichu.Position).forEach(function (key) {
      var side = tichu.Position[key];
      if (editable.calls[side]) {
        score.calls.push({side: side, call: editable.calls[side]});
      }
    });
    return score;
  }

  angular.module("tichu-score-detail", ["ng", "ngMaterial"])
      .controller("ScoreDetailController", ScoreDetailController);
})(angular);