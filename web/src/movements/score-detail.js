"use strict";
(function(angular) {
  /**
   * Main controller for the tournament list page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {$log} $log
   * @param {$mdDialog} $mdDialog
   * @param {$location} $location
   * @param {$window} $window
   * @param {TichuMovementService} TichuMovementService
   * @param {{pairCode: ?string, hand: !tichu.Hand, position: tichu.PairPosition, tournamentId: string}} loadResults
   * @ngInject
   */
  function ScoreDetailController($scope, $log, $mdDialog, $location, $window, TichuMovementService, loadResults) {
    /**
     * The scope this controller is attached to.
     * @type {angular.Scope}
     * @private
     */
    this._$scope = $scope;

    /**
     * Pair code used.
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
     * The change log for this hand.
     * @type {tichu.ChangeLog}
     * @export
     */ 
    this.changeLog = null;

    /**
     * The results of all scored hands for this hand number. If set the results
     * will be shown.
     * @type {tichu.HandResults}
     * @export
     */
    this.handResults = null;

    /**
     * Whether non-directors are allowed to overwrite scored hands.
     * @type {boolean}
     * @export
     */
    this.allowScoreOverwrites = loadResults.allowScoreOverwrites;

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
     * Whether we are asking the user to confirm a scoring operation.
     * @type {boolean}
     * @export
     */
     this.confirmingScore = false;
     
     /**
     * Whether a hand result getting operation is in progress.
     * @type {boolean}
     * @export
     */
     this.gettingHandResults = false;

    /**
     * The error resulting from the last save or delete operation.
     * @type {?tichu.RpcError}
     * @export
     */
    this.saveError = null;
    
    /**
     * Whether the change log is currently loading.
     * @type {boolean}
     * Export
     */
    this.loadingChangeLog = false;

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
    
    /**
     * The log service injected at creation.
     *
     * @private
     * @type {angular.$log}
     */
    this._$log = $log;
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
    if (this.saving || this.loadingChangeLog || this.saveFailure || 
        this.gettingHandResults ||
        (this.hand.score && !this.deleting && !this.overwriting)) {
      return;
    }
    this.confirmingScore = false;
    this.saving = true;
    var promise;
    if (this.deleting) {
      promise = this._movementService.clearScore(
          this._tournamentId,
          this.hand.northSouthPair.pairNo,
          this.hand.eastWestPair.pairNo,
          this.hand.handNo,
          this.pairCode);
    } else {
      promise = this._movementService.recordScore(
          this._tournamentId,
          this.hand.northSouthPair.pairNo,
          this.hand.eastWestPair.pairNo,
          this.hand.handNo,
          convertEditableToScore(this.score),
          this.pairCode);
    }
    var $mdDialog = this._$mdDialog;
    var self = this;
    promise.then(function() {
      if (self.allowScoreOverwrites || !this.pairCode) {
        $mdDialog.hide();
      } else {
        self.saving = false;
        self.overwriting = false;
      }
    }).catch(function(rejection) {
      self.saving = false;
      if (rejection.updatedState) {
        self.overwriting = false
        // This rejection means we are not allowed to overwrite scores. Set that
        // to false just in case we this fact changed while we were showing the 
        // dialog.
        self.allowScoreOverwrites = false;
        self.score = convertScoreToEditable(self.hand.score);
      } else {
        self.saveError = rejection;
      }
    });
  };

  /**
   * Loads the changeLog for a hand.
   */
  ScoreDetailController.prototype.loadChangeLog = function loadChangeLog() {
    if (this.saving || this.deleting || this.confirmingScore || 
        this.loadingChangeLog || this.gettingHandResults) {
      return;
    }
    this.loadingChangeLog = true;
    var self = this;
    this._movementService.getChangeLog(this._tournamentId,
                                       this.hand.handNo,
                                       this.hand.northSouthPair.pairNo, 
                                       this.hand.eastWestPair.pairNo)
        .then(function(response) {
          self.handResults = null;
          self.loadingChangeLog = false;
          self.changeLog = response;
        });
  }
  
  /**
   * Loads the hand results for a hand.
   */
  ScoreDetailController.prototype.getHandResults = function getHandResults() {
    if (this.saving || this.deleting || this.confirmingScore ||
        this.loadingChangeLog || this.gettingHandResults) {
      return;
    }
    this.gettingHandResults = true;
    var self = this;
    this._movementService.getHandResults(this._tournamentId,
                                         this.hand.handNo,
                                         this.pairCode)
        .then(function(response) {
            self.changeLog = null;
            self.handResults = response;
            self.gettingHandResults = false;
        });
  }
  
  /**
   * Clears changeLog and hand results info for this hand.
   */
  ScoreDetailController.prototype.closeSecondaryInfo = function closeSecondaryInfo() {
    this.changeLog = null;
    this.handResults = null;
  }
  
  /**
   * Returns true iff an RPC is in motion through saving, deleting, or
   * loading change logs and hand results.
   */
  ScoreDetailController.prototype.isLoading = function isLoading() {
    return this.saving || this.loadingChangeLogs || this.gettingHandResults;
  }

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
    if (!editable) {
      return null;
    }
    var score = new tichu.HandScore();
    var parsedNorthSouthScore = parseInt(editable.northSouthScore);
    var parsedEastWestScore = parseInt(editable.eastWestScore);
    score.northSouthScore = isNaN(parsedNorthSouthScore) ? editable.northSouthScore : parsedNorthSouthScore;
    score.eastWestScore = isNaN(parsedEastWestScore) ? editable.eastWestScore : parsedEastWestScore;
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
      .controller("ScoreDetailController", ScoreDetailController)
      .filter("reverse", function() {
        return function(items, position) {
          if (position == "N") {
            return items;
          };
          return items.slice().reverse();
        };
      })
      .filter("formatCalls", function() {
        return function(calls, position) {
          if (calls === null || calls.length == 0) {
            return "(No Calls)";
          }
          var stringCalls = "(";
          for (i = 0; i < calls.length; i++) {
            var call = calls[i];
            if (position == "N" && (call.side.toUpperCase() == "EAST" || call.side.toUpperCase() == "WEST")) {
              continue;
            }
            if (position == "E" && (call.side.toUpperCase() == "NORTH" || call.side.toUpperCase() == "SOUTH")) {
              continue;
            }
            if (stringCalls.length > 1) {
              return stringCalls + ", " + call.call + ")";
            }
            stringCalls = stringCalls + call.call;
          }
          if (stringCalls.length > 1) {
            return stringCalls + ")";
          }
          return "(No Calls)";
        }
      });
})(angular);