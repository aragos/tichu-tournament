"use strict";
(function(angular) {
  /**
   * Main controller for the tournament list page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {$mdDialog} $mdDialog
   * @param {boolean} usedPairCode
   * @param {!tichu.Hand} hand
   * @param {string} position
   * @ngInject
   */
  function ScoreDetailController($scope, $mdDialog, usedPairCode, hand, position) {
    /**
     * The scope this controller is attached to.
     * @type {angular.Scope}
     * @private
     */
    this._$scope = $scope;

    /**
     * Whether a pair code was used.
     * @type {boolean}
     * @export
     */
    this.usedPairCode = usedPairCode;

    /**
     * The hand being displayed.
     * @type {!tichu.Hand}
     * @export
     */
    this.hand = hand;

    /**
     * The position to be displayed.
     * @type {string}
     * @export
     */
    this.position = position;

    /**
     * The current edited form of the score.
     * @type {{northSouthScore: number, eastWestScore: number, calls: Object.<tichu.Position, tichu.Call>, notes: string}}
     * @export
     */
    this.score = convertScoreToEditable(this.hand.score);

    /**
     * Whether the user has elected to delete the score instead.
     * @type {boolean}
     * @export
     */
    this.deleting = false;

    /**
     * The dialog service used to close the dialog.
     * @type {$mdDialog}
     * @private
     */
    this._$mdDialog = $mdDialog;
  }

  /**
   * Closes the dialog without saving.
   * @export
   */
  ScoreDetailController.prototype.cancel = function cancel() {
    this._$mdDialog.cancel();
  };

  /**
   * Closes the dialog and saves the result.
   * @export
   */
  ScoreDetailController.prototype.save = function cancel() {
    this._$mdDialog.hide(this.deleting ? null : convertEditableToScore(this.score));
  };

  /**
   * Converts the given score to an easily editable format.
   * @param {!tichu.HandScore} score
   * @returns {!{northSouthScore: number, eastWestScore: number, calls: Object<tichu.Position, tichu.Call>, notes: string}}
   */
  function convertScoreToEditable(score) {
    if (!score) {
      return {
        northSouthScore: 0,
        eastWestScore: 0,
        calls: {},
        notes: ""
      };
    }
    var convertedCalls = {};
    score.calls.forEach(function(call) {
      convertedCalls[call.side] = call.call;
    });
    return {
      northSouthScore: score.northSouthScore,
      eastWestScore: score.eastWestScore,
      calls: convertedCalls,
      notes: score.notes
    };
  }

  /**
   *
   * @param {!{northSouthScore: number, eastWestScore: number, calls: Object<tichu.Position, tichu.Call>, notes: string}} editable
   * @returns {!tichu.HandScore}
   */
  function convertEditableToScore(editable) {
    var score = new tichu.HandScore();
    score.northSouthScore = editable.northSouthScore;
    score.eastWestScore = editable.eastWestScore;
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