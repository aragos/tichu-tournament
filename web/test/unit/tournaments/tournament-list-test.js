"use strict";
describe("tichu-tournament-list module", function() {
  beforeEach(module("tichu-tournament-list"));

  describe("TournamentListController controller", function() {
    var scope;
    var header;
    var tournamentListController;

    beforeEach(inject(function(/** angular.Scope */ $rootScope,
                               /** angular.$controller */ $controller) {
      var appScope = $rootScope.$new(false);
      appScope.appController = {
        setPageHeader: function(_header_) {
          header = _header_;
        }
      };
      scope = appScope.$new(false);
      tournamentListController =
          $controller("TournamentListController as tournamentListController", {
            "$scope": scope,
            "tournaments": [{
              "id": "12345",
              "name": "turn"
            }]});
    }));

    it("sets a header", function() {
      expect(header.header).toBe("Tournaments");
      expect(header.backPath).toBe("/home");
      expect(header.showHeader).toBe(true);
    });

    it("has some tournaments", function() {
      expect(tournamentListController.tournaments.length).toBeGreaterThan(0);
      expect(tournamentListController.tournaments[0].name).toBeDefined();
      expect(tournamentListController.tournaments[0].id).toBeDefined();
    });
  });
});