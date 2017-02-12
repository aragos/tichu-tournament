"use strict";
describe("code-service module", function() {
  var $httpBackend, $rootScope;

  beforeEach(module("tichu-code-service"));

  beforeEach(inject(function(_$httpBackend_, _$rootScope_) {
    $httpBackend = _$httpBackend_;
    $rootScope = _$rootScope_;
  }));

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation();
    $httpBackend.verifyNoOutstandingRequest();
  });

  describe("TichuCodeService", function() {
    var service;
    /** @type {PromiseHelper} */
    var runPromise;

    beforeEach(inject(function (TichuCodeService) {
      service = TichuCodeService;
      runPromise = promiseHelper($rootScope, $httpBackend);
    }));

    describe("getMovementForCode", function() {
      it("sends the pair ID as the last parameter of the URL", function() {
        $httpBackend.expectGET('/api/tournaments/pairno/CODY')
            .respond(200, "I actually don't care what you think");
        runPromise(service.getMovementForCode("CODY"), {flushHttp: true});
      });

      it("calls the server again on each call", function() {
        $httpBackend.expectGET('/api/tournaments/pairno/COOL')
            .respond(200, "I actually don't care what you think");
        runPromise(service.getMovementForCode("COOL"), {flushHttp: true});
        $httpBackend.expectGET('/api/tournaments/pairno/COOL')
            .respond(200, "I actually don't care what you think");
        runPromise(service.getMovementForCode("COOL"), {flushHttp: true});
      });

      it("resolves the promise with an ID and pair number on success", function() {
        $httpBackend.expectGET('/api/tournaments/pairno/YESS')
            .respond(200, {
              "tournament_infos": [{
                "pair_no": 7,
                "tournament_id": "7777"
              }]
            });
        var result = runPromise(service.getMovementForCode("YESS"), {flushHttp: true, expectSuccess: true});
        expect(result.tournamentId).toBe("7777");
        expect(result.pairNo).toBe(7);
      });

      it("rejects the promise in case of an error", function() {
        $httpBackend.expectGET('/api/tournaments/pairno/NOOO')
            .respond(500, {
              "error": "I just don't like your face",
              "detail": "Seriously, did you get that at the... ugly factory..."
            });
        var result = runPromise(service.getMovementForCode("NOOO"), {flushHttp: true, expectFailure: true});
        expect(result.redirectToLogin).toBe(false);
        expect(result.error).toBe("I just don't like your face");
        expect(result.detail).toBe("Seriously, did you get that at the... ugly factory...");
      });

      it("rejects the promise in case of a 404", function() {
        $httpBackend.expectGET('/api/tournaments/pairno/WTFS')
            .respond(404, {
              "error": "What code even is that",
              "detail": "You can't just make shit up you know"
            });
        var result = runPromise(service.getMovementForCode("WTFS"), {flushHttp: true, expectFailure: true});
        expect(result.redirectToLogin).toBe(false);
      });

      it("rejects the promise in the unlikely case that the list is empty", function() {
        $httpBackend.expectGET('/api/tournaments/pairno/UMMM')
            .respond(200, {
              "tournament_infos": []
            });
        var result = runPromise(service.getMovementForCode("UMMM"), {flushHttp: true, expectFailure: true});
        expect(result.redirectToLogin).toBe(false);
        expect(result.error).toBeDefined();
        expect(result.detail).toBeDefined();
      });

      it("rejects the promise in the unlikely case that the list has 2+ items in it", function() {
        $httpBackend.expectGET('/api/tournaments/pairno/OOPS')
            .respond(200, {
              "tournament_infos": [{
                "pair_no": 6,
                "tournament_id": "6969"
              }, {
                "pair_no": 9,
                "tournament_id": "9696"
              }]
            });
        var result = runPromise(service.getMovementForCode("OOPS"), {flushHttp: true, expectFailure: true});
        expect(result.redirectToLogin).toBe(false);
        expect(result.error).toBeDefined();
        expect(result.detail).toBeDefined();
      });
    });
  });
});