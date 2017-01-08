"use strict";
describe("tichu-movement-detail module", function() {
  beforeEach(module("tichu-movement-detail"));

  describe("MovementDetailController controller", function() {
    var scope;
    var $rootScope;
    var header;
    var $controller;
    var $route;
    var $mdDialog;
    var $location;
    var $window;
    var dialogDeferred;

    beforeEach(module(function($provide) {
      $window = {location: {href: "/tournaments/123456/movement/7"}};
      $provide.value("$window", $window);
    }));

    beforeEach(inject(function(/** angular.Scope */ _$rootScope_,
                               /** angular.$q */ $q,
                               /** angular.$controller */ _$controller_,
                               /** $route */ _$route_,
                               /** angular.$location */ _$location_,
                               /** $mdDialog */ _$mdDialog_) {
      $rootScope = _$rootScope_;
      var appScope = $rootScope.$new(false);
      appScope.appController = {
        setPageHeader: function(_header_) {
          header = _header_;
        }
      };
      scope = appScope.$new(false);
      $controller = _$controller_;
      $route = _$route_;
      $location = _$location_;
      $mdDialog = _$mdDialog_;
      spyOn($route, "reload");
      spyOn($mdDialog, "show").and.callFake(function (presets) {
        dialogDeferred = $q.defer();
        return dialogDeferred.promise;
      });
      spyOn($mdDialog, "hide").and.callFake(function (result) {
        dialogDeferred.resolve(result);
      });
      spyOn($mdDialog, "cancel").and.callFake(function (result) {
        dialogDeferred.reject(result);
      })
    }));

    /**
     * Starts up the controller with the given load results.
     *
     * @param {Object=} results
     * @returns {MovementDetailController}
     */
    function loadController(results) {
      return $controller("MovementDetailController as movementDetailController", {
        "$scope": scope,
        "loadResults": results || {
          pairCode: null,
          movement: new tichu.Movement(
              new tichu.TournamentHeader("123456"),
              new tichu.TournamentPair(7))
        }
      });
    }

    it("sets a header which goes back to the tournament if no code was used", function() {
      var tournamentHeader = new tichu.TournamentHeader("123456789");
      tournamentHeader.name = "my tournament";
      var pair = new tichu.TournamentPair(7);
      var movement = new tichu.Movement(tournamentHeader, pair);
      loadController({
        pairCode: null,
        movement: movement
      });
      expect(header.header).toBe("Pair #7 - my tournament");
      expect(header.backPath).toBe("/tournaments/123456789");
      expect(header.showHeader).toBe(true);
    });

    it("sets backPath to /home if a code was used", function() {
      var tournamentHeader = new tichu.TournamentHeader("123456789");
      tournamentHeader.name = "my tournament";
      var pair = new tichu.TournamentPair(7);
      var movement = new tichu.Movement(tournamentHeader, pair);
      loadController({
        pairCode: "CODE",
        movement: movement
      });
      expect(header.backPath).toBe("/home");
    });

    it("has a movement and code from the load results", function() {
      var tournamentHeader = new tichu.TournamentHeader("123456789");
      tournamentHeader.name = "my tournament";
      var pair = new tichu.TournamentPair(7);
      var movement = new tichu.Movement(tournamentHeader, pair);
      var movementDetailController = loadController({
        pairCode: "CODE",
        movement: movement
      });
      expect(movementDetailController.playerCode).toBe("CODE");
      expect(movementDetailController.movement).toBe(movement);
    });

    it("exposes an editHand method which opens a dialog and sends the hand", function() {
      var tournamentHeader = new tichu.TournamentHeader("123456789");
      tournamentHeader.name = "my tournament";
      var pair = new tichu.TournamentPair(7);
      var movement = new tichu.Movement(tournamentHeader, pair);
      var controller = loadController({
        pairCode: null,
        movement: movement
      });

      var round = new tichu.MovementRound();
      round.position = tichu.PairPosition.EAST_WEST;
      var hand = new tichu.Hand(1, 2, 3);
      controller.editHand(round, hand);

      expect($mdDialog.show).toHaveBeenCalled();
      var settings = $mdDialog.show.calls.mostRecent().args[0];
      expect(settings.locals.loadResults.tournamentId).toBe("123456789");
      expect(settings.locals.loadResults.position).toBe(tichu.PairPosition.EAST_WEST);
      expect(settings.locals.loadResults.hand).toBe(hand);
      expect(settings.locals.loadResults.pairCode).toBe(null);
    });

    it("sends pairCode with editHand if a pair code was set", function() {
      var tournamentHeader = new tichu.TournamentHeader("123456789");
      tournamentHeader.name = "my tournament";
      var pair = new tichu.TournamentPair(7);
      var movement = new tichu.Movement(tournamentHeader, pair);
      var controller = loadController({
        pairCode: "APER",
        movement: movement
      });

      var round = new tichu.MovementRound();
      round.position = tichu.PairPosition.EAST_WEST;
      var hand = new tichu.Hand(1, 2, 3);
      controller.editHand(round, hand);

      expect($mdDialog.show).toHaveBeenCalled();
      var settings = $mdDialog.show.calls.mostRecent().args[0];
      expect(settings.locals.loadResults.pairCode).toBe('APER');
    });

    it("displays a dialog in case of error", function() {
      loadController({
        pairCode: null,
        failure: {
          redirectToLogin: false,
          error: "An error happened",
          detail: "It was a very erroneous error"
        }
      });
      expect($mdDialog.show).toHaveBeenCalled();
    });

    it("reloads the page when the dialog is OK'd", function() {
      loadController({
        pairCode: null,
        failure: {
          redirectToLogin: false,
          error: "An error happened",
          detail: "It was a very erroneous error"
        }
      });
      dialogDeferred.resolve();
      $rootScope.$apply();
      expect($route.reload).toHaveBeenCalled();
    });

    it("leaves for /home when the dialog is canceled", function() {
      loadController({
        pairCode: null,
        failure: {
          redirectToLogin: false,
          error: "An error happened",
          detail: "It was a very erroneous error"
        }
      });
      dialogDeferred.reject();
      $rootScope.$apply();
      expect($location.url()).toBe("/home");
    });

    it("opens the login page when the dialog is OK'd on a login error", function() {
      $location.url("/tournaments/123456/movement/7");
      loadController({
        pairCode: null,
        failure: {
          redirectToLogin: true,
          error: "Log in already",
          detail: "What are you even doing here"
        }
      });
      dialogDeferred.resolve();
      $rootScope.$apply();
      expect($window.location.href).toBe("/api/login?then=%2Ftournaments%2F123456%2Fmovement%2F7");
    });

    it("returns /home when the dialog is OK'd on a login error if a code was set", function() {
      $location.url("/tournaments/123456/movement/7?playerCode=CODE");
      loadController({
        pairCode: "CODE",
        failure: {
          redirectToLogin: true,
          error: "Log in already",
          detail: "What are you even doing here"
        }
      });
      dialogDeferred.resolve();
      $rootScope.$apply();
      expect($location.url()).toBe("/home");
    });

    it("cancels the dialog and doesn't change URLs when the scope is destroyed", function() {
      $location.url("/tournaments/123456/movement/7");
      loadController({
        failure: {
          redirectToLogin: false,
          error: "An error happened",
          detail: "It was a very erroneous error"
        }
      });
      scope.$destroy();
      expect($mdDialog.cancel).toHaveBeenCalled();
      $rootScope.$apply();
      expect($location.url()).toBe("/tournaments/123456/movement/7");
    })
  });
});