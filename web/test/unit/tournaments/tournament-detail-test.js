"use strict";
describe("tichu-tournament-detail module", function() {
  beforeEach(module("tichu-tournament-detail"));

  describe("TournamentDetailController controller", function() {
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
      $window = {location: {href: "/tournaments/123456"}};
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
     * @returns {TournamentListController}
     */
    function loadController(results) {
      return $controller("TournamentDetailController as tournamentDetailController", {
        "$scope": scope,
        "loadResults": results || {
          tournament: new tichu.Tournament(new tichu.TournamentHeader("123456"))
        }
      });
    }

    it("sets a header", function() {
      var tournamentHeader = new tichu.TournamentHeader("123456789");
      tournamentHeader.name = "my tournament";
      var tournament = new tichu.Tournament(tournamentHeader);
      loadController({
        tournament: tournament
      });
      expect(header.header).toBe("my tournament");
      expect(header.backPath).toBe("/tournaments");
      expect(header.showHeader).toBe(true);
    });

    it("has a tournament with a name and ID and some pairs", function() {
      var tournamentHeader = new tichu.TournamentHeader("123456789");
      tournamentHeader.name = "a tournament";
      var tournament = new tichu.Tournament(tournamentHeader);
      var tournamentDetailController = loadController({
        tournament: tournament
      });
      expect(tournamentDetailController.tournament).toBe(tournament);
    });

    it("displays a dialog in case of error", function() {
      loadController({
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
      $location.url("/tournaments/123456");
      loadController({
        failure: {
          redirectToLogin: true,
          error: "Log in already",
          detail: "What are you even doing here"
        }
      });
      dialogDeferred.resolve();
      $rootScope.$apply();
      expect($window.location.href).toBe("/api/login?then=%2Ftournaments%2F123456");
    });

    it("cancels the dialog and doesn't change URLs when the scope is destroyed", function() {
      $location.url("/tournaments/123456");
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
      expect($location.url()).toBe("/tournaments/123456");
    })
  });
});