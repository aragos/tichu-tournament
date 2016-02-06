"use strict";
describe("tichu-tournament-list module", function() {
  beforeEach(module("tichu-tournament-list"));

  describe("TournamentListController controller", function() {
    var scope;
    var appController;
    var tournamentListController;

    beforeEach(inject(function(/** angular.Scope */ $rootScope,
                               /** angular.$controller */ $controller) {
      var appScope = $rootScope.$new(false);
      appController = {"header": ""};
      appScope.appController = appController;
      scope = appScope.$new(false);
      tournamentListController =
          $controller("TournamentListController as tournamentListController", {"$scope": scope});
    }));

    it("sets a header", function() {
      expect(appController.header).toBe("Tournaments");
    });

    it("has some tournaments", function() {
      expect(tournamentListController.tournaments.length).toBeGreaterThan(0);
      expect(tournamentListController.tournaments[0].name).toBeDefined();
      expect(tournamentListController.tournaments[0].id).toBeDefined();
    });
  });
});