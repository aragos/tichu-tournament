"use strict";
describe("tichu-score-detail module", function () {
  beforeEach(module("tichu-score-detail"));

  describe("ScoreDetailController controller", function () {
    var scope;
    var $rootScope;
    var $controller;
    var $mdDialog;
    var $window;
    var $location;
    var movementService;

    beforeEach(module(function ($provide) {
      $window = {location: {href: "/tournaments/123456/movement/7"}};
      $provide.value("$window", $window);
      $provide.service("TichuMovementService", function ($q) {
        return {
          recordedScores: [],
          recordScore: function recordScore(tournamentId, nsPair, ewPair, handNo, score, pairCode) {
            var deferred = $q.defer();
            this.recordedScores.push({
              params: {
                tournamentId: tournamentId,
                nsPair: nsPair,
                ewPair: ewPair,
                handNo: handNo,
                score: score,
                pairCode: pairCode
              },
              deferred: deferred
            });
            return deferred.promise;
          },
          clearedScores: [],
          clearScore: function clearScore(tournamentId, nsPair, ewPair, handNo, pairCode) {
            var deferred = $q.defer();
            this.clearedScores.push({
              params: {
                tournamentId: tournamentId,
                nsPair: nsPair,
                ewPair: ewPair,
                handNo: handNo,
                pairCode: pairCode
              },
              deferred: deferred
            });
            return deferred.promise;
          }
        };
      });
    }));

    beforeEach(inject(function (/** angular.Scope */ _$rootScope_,
                                /** angular.$q */ $q,
                                /** angular.$controller */ _$controller_,
                                /** $mdDialog */ _$mdDialog_,
                                /** $location */ _$location_,
                                /** TichuMovementService */ TichuMovementService) {
      $rootScope = _$rootScope_;
      scope = $rootScope.$new(false);
      $controller = _$controller_;
      $mdDialog = _$mdDialog_;
      $location = _$location_;
      movementService = TichuMovementService;
      spyOn($mdDialog, "hide");
      spyOn($mdDialog, "cancel");
    }));

    /**
     * Starts up the controller with the given configuration.
     *
     * @param {{hand: tichu.Hand=, pairCode: string=, position: tichu.PairPosition=, tournamentId: string=}=} settings
     * @returns {ScoreDetailController}
     */
    function loadController(settings) {
      return $controller("ScoreDetailController as scoreDetailController", {
        "$scope": scope,
        "loadResults": {
          pairCode: (settings && settings.pairCode) || null,
          hand: (settings && settings.hand) || new tichu.Hand(1, 2, 3),
          position: (settings && settings.position) || tichu.PairPosition.NORTH_SOUTH,
          tournamentId: (settings && settings.tournamentId) || "123456"
        }
      });
    }

    it("exposes the pairCode value on itself", function () {
      var controller = loadController({pairCode: "HOPS"});
      expect(controller.pairCode).toBe("HOPS");
    });

    it("exposes the hand value on itself", function () {
      var hand = new tichu.Hand(1, 2, 3);
      var controller = loadController({hand: hand});
      expect(controller.hand).toBe(hand);
    });

    it("exposes the position value on itself", function () {
      var controller = loadController({position: tichu.PairPosition.NORTH_SOUTH});
      expect(controller.position).toBe(tichu.PairPosition.NORTH_SOUTH);
    });

    it("exposes an empty score object if the hand had no score", function () {
      var hand = new tichu.Hand(1, 2, 3);
      var controller = loadController({hand: hand});

      expect(typeof controller.score.northSouthScore).toBe("string");
      expect(typeof controller.score.eastWestScore).toBe("string");
      expect(typeof controller.score.notes).toBe("string");
      expect(typeof controller.score.calls).toBe("object");
    });

    it("exposes a score object based on the hand's score", function () {
      var score = new tichu.HandScore();
      score.northSouthScore = 25;
      score.eastWestScore = 175;
      score.calls = [{side: tichu.Position.EAST, call: tichu.Call.TICHU}];
      score.notes = "what a call";
      var hand = new tichu.Hand(1, 2, 3);
      hand.score = score;
      var controller = loadController({hand: hand});

      var expectedCalls = {};
      expectedCalls[tichu.Position.EAST] = tichu.Call.TICHU;
      expect(controller.score).not.toBe(score);
      expect(controller.score).toEqual({
        northSouthScore: "25",
        eastWestScore: "175",
        calls: expectedCalls,
        notes: "what a call"
      });
    });

    it("exposes a cancel method which cancels the dialog", function () {
      var controller = loadController();
      controller.cancel();
      expect($mdDialog.cancel).toHaveBeenCalled();
    });

    it("exposes a save method which calls the score saving service", function () {
      var controller = loadController({
        tournamentId: "989898",
        position: tichu.PairPosition.NORTH_SOUTH,
        hand: new tichu.Hand(1, 2, 4),
        pairCode: "FOOP"
      });
      controller.score.northSouthScore = 25;
      controller.score.eastWestScore = 175;
      controller.score.calls[tichu.Position.EAST] = tichu.Call.TICHU;
      controller.score.notes = "what a call";
      controller.save();

      var expectedScore = new tichu.HandScore();
      expectedScore.northSouthScore = 25;
      expectedScore.eastWestScore = 175;
      expectedScore.calls = [{side: tichu.Position.EAST, call: tichu.Call.TICHU}];
      expectedScore.notes = "what a call";
      expect(controller.saving).toBe(true);
      expect(controller.deleting).toBe(false);
      expect(movementService.clearedScores).toEqual([]);
      expect(movementService.recordedScores.length).toBe(1);
      expect(movementService.recordedScores[0].params).toEqual({
        tournamentId: "989898",
        nsPair: 1,
        ewPair: 2,
        handNo: 4,
        score: expectedScore,
        pairCode: "FOOP"
      });
    });

    it("exposes a deleting variable which causes save to clear the score instead", function () {
      var controller = loadController({
        tournamentId: "989898",
        position: tichu.PairPosition.NORTH_SOUTH,
        hand: new tichu.Hand(1, 2, 4),
        pairCode: "FOOP"
      });
      expect(controller.deleting).toBe(false);
      controller.deleting = true;
      controller.save();

      expect(controller.saving).toBe(true);
      expect(controller.deleting).toBe(true);
      expect(movementService.recordedScores).toEqual([]);
      expect(movementService.clearedScores.length).toBe(1);
      expect(movementService.clearedScores[0].params).toEqual({
        tournamentId: "989898",
        nsPair: 1,
        ewPair: 2,
        handNo: 4,
        pairCode: "FOOP"
      });
    });

    it("automatically closes the dialog after the save operation completes", function () {
      var controller = loadController({
        tournamentId: "989898",
        position: tichu.PairPosition.NORTH_SOUTH,
        hand: new tichu.Hand(1, 2, 4),
        pairCode: "FOOP"
      });
      controller.save();

      movementService.recordedScores[0].deferred.resolve();
      $rootScope.$apply();
      expect(controller.saving).toBe(true);
      expect($mdDialog.hide).toHaveBeenCalled();
    });

    it("switches to failed mode if the save operation fails", function () {
      var controller = loadController({
        tournamentId: "989898",
        position: tichu.PairPosition.NORTH_SOUTH,
        hand: new tichu.Hand(1, 2, 4),
        pairCode: "FOOP"
      });
      controller.save();

      var error = new tichu.RpcError();
      error.redirectToLogin = false;
      error.error = "you screwed the pooch";
      error.detail = "saving blew it";
      movementService.recordedScores[0].deferred.reject(error);
      $rootScope.$apply();
      expect(controller.saving).toBe(false);
      expect(controller.saveError).toBe(error);
      expect($mdDialog.hide).not.toHaveBeenCalled();
    });

    it("offers a goHome method to return to the code entry screen if the save operation fails", function () {
      $location.url("/tournament/989898/movement/2?playerCode=RONG");
      var controller = loadController({
        tournamentId: "989898",
        position: tichu.PairPosition.NORTH_SOUTH,
        hand: new tichu.Hand(1, 2, 4),
        pairCode: "RONG"
      });
      controller.save();

      var error = new tichu.RpcError();
      error.redirectToLogin = true;
      error.error = "your code is rong";
      error.detail = "so no saving for you";
      movementService.recordedScores[0].deferred.reject(error);
      $rootScope.$apply();
      controller.goHome();
      expect($mdDialog.cancel).toHaveBeenCalled();
      expect($location.url()).toBe("/home");
    });

    it("offers a login method to return to the login screen if the save operation fails", function () {
      $location.url("/tournament/989898/movement/2");
      var controller = loadController({
        tournamentId: "989898",
        position: tichu.PairPosition.NORTH_SOUTH,
        hand: new tichu.Hand(1, 2, 4),
        pairCode: "RONG"
      });
      controller.save();

      var error = new tichu.RpcError();
      error.redirectToLogin = true;
      error.error = "you're not logged in";
      error.detail = "so no saving for you";
      movementService.recordedScores[0].deferred.reject(error);
      $rootScope.$apply();
      controller.login();
      expect($mdDialog.cancel).toHaveBeenCalled();
      expect($window.location.href).toBe("/api/login?then=%2Ftournament%2F989898%2Fmovement%2F2");
    });

    it("offers a tryAgain method to return to the edit form if the save operation fails", function () {
      $location.url("/tournament/989898/movement/2");
      var controller = loadController({
        tournamentId: "989898",
        position: tichu.PairPosition.NORTH_SOUTH,
        hand: new tichu.Hand(1, 2, 4),
        pairCode: "RONG"
      });
      controller.save();

      var error = new tichu.RpcError();
      error.redirectToLogin = true;
      error.error = "you're not logged in";
      error.detail = "so no saving for you";
      movementService.recordedScores[0].deferred.reject(error);
      $rootScope.$apply();
      controller.tryAgain();
      expect(controller.saveError).toBeNull();
      expect(controller.saving).toBe(false);
    });
  });
});
