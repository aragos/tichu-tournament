"use strict";
describe("tichu-score-detail module", function() {
  beforeEach(module("tichu-score-detail"));

  describe("ScoreDetailController controller", function() {
    var scope;
    var $rootScope;
    var $controller;
    var $mdDialog;
    var $window;

    beforeEach(module(function($provide) {
      $window = {location: {href: "/tournaments/123456/movement/7"}};
      $provide.value("$window", $window);
    }));

    beforeEach(inject(function(/** angular.Scope */ _$rootScope_,
                               /** angular.$q */ $q,
                               /** angular.$controller */ _$controller_,
                               /** $mdDialog */ _$mdDialog_) {
      $rootScope = _$rootScope_;
      scope = $rootScope.$new(false);
      $controller = _$controller_;
      $mdDialog = _$mdDialog_;
      spyOn($mdDialog, "hide");
      spyOn($mdDialog, "cancel");
    }));

    /**
     * Starts up the controller with the given hand to edit.
     *
     * @param {tichu.Hand=} hand
     * @param {boolean=} usedPairCode
     * @returns {ScoreDetailController}
     */
    function loadController(hand, usedPairCode, position) {
      return $controller("ScoreDetailController as scoreDetailController", {
        "$scope": scope,
        "usedPairCode": usedPairCode || false,
        "hand": hand || new tichu.Hand(1, 2, 3),
        "position": position || tichu.PairPosition.NORTH_SOUTH
      });
    }

    it("exposes the usedPairCode value on itself", function() {
      var controller = loadController(undefined, true);
      expect(controller.usedPairCode).toBe(true);
    });

    it("exposes the hand value on itself", function() {
      var hand = new tichu.Hand(1, 2, 3);
      var controller = loadController(hand);
      expect(controller.hand).toBe(hand);
    });

    it("exposes the position value on itself", function() {
      var controller = loadController(undefined, undefined, tichu.PairPosition.NORTH_SOUTH);
      expect(controller.position).toBe(tichu.PairPosition.NORTH_SOUTH);
    });

    it("exposes an empty score object if the hand had no score", function() {
      var hand = new tichu.Hand(1, 2, 3);
      var controller = loadController(hand);

      expect(typeof controller.score.northSouthScore).toBe("number");
      expect(typeof controller.score.eastWestScore).toBe("number");
      expect(typeof controller.score.notes).toBe("string");
      expect(typeof controller.score.calls).toBe("object");
    });

    it("exposes a score object based on the hand's score", function() {
      var score = new tichu.HandScore();
      score.northSouthScore = 25;
      score.eastWestScore = 175;
      score.calls = [{side: tichu.Position.EAST, call: tichu.Call.TICHU}];
      score.notes = "what a call";
      var hand = new tichu.Hand(1, 2, 3);
      hand.score = score;
      var controller = loadController(hand);

      var expectedCalls = {};
      expectedCalls[tichu.Position.EAST] = tichu.Call.TICHU;
      expect(controller.score).not.toBe(score);
      expect(controller.score).toEqual({
        northSouthScore: 25,
        eastWestScore: 175,
        calls: expectedCalls,
        notes: "what a call"
      });
    });

    it("exposes a cancel method which cancels the dialog", function() {
      var controller = loadController();
      controller.cancel();
      expect($mdDialog.cancel).toHaveBeenCalled();
    });

    it("exposes a deleting variable which causes save to return null", function() {
      var controller = loadController();
      expect(controller.deleting).toBe(false);
      controller.deleting = true;
      controller.save();
      expect($mdDialog.hide).toHaveBeenCalledWith(null);
    });

    it("exposes a save method which closes the dialog and returns the converted score object", function() {
      var controller = loadController();
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
      expect($mdDialog.hide).toHaveBeenCalledWith(expectedScore);
    });
  });
});