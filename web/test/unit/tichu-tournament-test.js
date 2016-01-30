describe("tichu-tournament module", function() {
  beforeEach(module("tichu-tournament"));

  it("sets tichu on the $rootScope", inject(function($rootScope) {
    expect($rootScope.tichu).toBe("Grand Tichu");
  }));
});