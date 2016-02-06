"use strict";
describe("tichu-tournament module", function() {
  beforeEach(module("tichu-tournament"));

  describe("AppController controller", function() {
    var scope;
    var appController;

    beforeEach(inject(function (/** angular.Scope */ $rootScope,
                                /** angular.$controller */ $controller) {
      scope = $rootScope.$new(false);
      appController = $controller("AppController as appController", {"$scope": scope});
    }));

    it("sets a header and title", function () {
      expect(appController.header).toBe("Tichu Tournament");
      expect(appController.title).toBe("Tichu Tournament");
    });
  });
});