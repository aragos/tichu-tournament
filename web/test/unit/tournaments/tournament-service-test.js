"use strict";
describe("tournament-service module", function() {
  var $httpBackend, $rootScope;

  beforeEach(module("tichu-tournament-service"));

  beforeEach(inject(function(_$httpBackend_, _$rootScope_) {
    $httpBackend = _$httpBackend_;
    $rootScope = _$rootScope_;
  }));

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation();
    $httpBackend.verifyNoOutstandingRequest();
  });

  describe("TichuTournamentService", function() {
    var service;

    beforeEach(inject(function(TichuTournamentService) {
      service = TichuTournamentService;
    }));

    it("downloads the tournament list on first call to getTournaments", function() {
      $httpBackend.expectGET('/api/tournaments')
          .respond(200, {
            "tournaments": [
              {"id": "123", "name": "My First Tournament"},
              {"id": "321", "name": "My Other Tournament"}
            ]
          });

      var tournamentList, failure;
      service.getTournaments().then(function(_tournamentList_) {
        tournamentList = _tournamentList_;
      }).catch(function(err) {
        failure = {
          promise_rejected_with: err
        };
      });
      $httpBackend.flush();  // causes the request to receive its response
      $rootScope.$apply();  // causes the promise to resolve

      expect(failure).toBeUndefined();
      expect(tournamentList.length).toEqual(2);
      expect(tournamentList[0].id).toEqual("123");
      expect(tournamentList[0].name).toEqual("My First Tournament");
      expect(tournamentList[1].id).toEqual("321");
      expect(tournamentList[1].name).toEqual("My Other Tournament");
    });

    it("returns the tournament list without a server call on subsequent calls", function() {
      $httpBackend.expectGET('/api/tournaments')
          .respond(200, {
            "tournaments": [
              {"id": "123", "name": "My First Tournament"},
              {"id": "321", "name": "My Other Tournament"}
            ]
          });

      var firstTournamentList, secondTournamentList, failure;
      service.getTournaments().then(function(_tournamentList_) {
        firstTournamentList = _tournamentList_;
      }).catch(function(err) {
        failure = {
          first_promise_rejected_with: err
        };
      });
      $httpBackend.flush();  // causes the request to receive its response
      $rootScope.$apply();  // causes the promise to resolve
      service.getTournaments().then(function(_tournamentList_) {
        secondTournamentList = _tournamentList_;
      }).catch(function(err) {
        failure = failure || {};
        failure.second_promise_rejected_with = err;
      });
      $httpBackend.verifyNoOutstandingRequest();
      $rootScope.$apply();

      expect(failure).toBeUndefined();
      expect(secondTournamentList).toBe(firstTournamentList);
    });

    it("rejects the returned promise if an error is returned", function() {
      $httpBackend.expectGET('/api/tournaments')
          .respond(500, {
            "error": "something baaaad",
            "detail": "is happening in Oz"
          });

      var tournamentList, rejection;
      service.getTournaments().then(function(_tournamentList_) {
        tournamentList = _tournamentList_;
      }).catch(function(err) {
        rejection = err;
      });
      $httpBackend.flush();  // causes the request to receive its response
      $rootScope.$apply();  // causes the promise to resolve

      expect(tournamentList).toBeUndefined();
      expect(rejection.redirectToLogin).toBe(false);
      expect(rejection.error).toBe("something baaaad");
      expect(rejection.detail).toBe("is happening in Oz");
    });

    it("sets redirectToLogin on the rejection for a 401", function() {
      $httpBackend.expectGET('/api/tournaments')
          .respond(401, {
            "error": "u not logged in",
            "detail": "get over to the login page"
          });

      var tournamentList, rejection;
      service.getTournaments().then(function(_tournamentList_) {
        tournamentList = _tournamentList_;
      }).catch(function(err) {
        rejection = err;
      });
      $httpBackend.flush();  // causes the request to receive its response
      $rootScope.$apply();  // causes the promise to resolve

      expect(tournamentList).toBeUndefined();
      expect(rejection.redirectToLogin).toBe(true);
    });

    it("doesn't cache error responses", function() {
      $httpBackend.expectGET('/api/tournaments')
          .respond(500, {
            "error": "something baaaad",
            "detail": "is happening in Oz"
          });

      service.getTournaments().catch(function() {
        // it's okay just ignore this
      });
      $httpBackend.flush();  // causes the request to receive its response
      $rootScope.$apply();  // causes the promise to resolve

      $httpBackend.expectGET('/api/tournaments')
          .respond(200, {
            "tournaments": [
              {"id": "123", "name": "My First Tournament"},
              {"id": "321", "name": "My Other Tournament"}
            ]
          });

      var tournamentList, rejection;
      service.getTournaments().then(function(_tournamentList_) {
        tournamentList = _tournamentList_;
      }).catch(function(err) {
        rejection = err;
      });
      $httpBackend.flush();  // causes the request to receive its response
      $rootScope.$apply();  // causes the promise to resolve

      expect(tournamentList).toBeDefined();
    });

    it("only makes one server call even if another call comes in before it returns", function() {
      $httpBackend.expectGET('/api/tournaments')
          .respond(200, {
            "tournaments": [
              {"id": "123", "name": "My First Tournament"},
              {"id": "321", "name": "My Other Tournament"}
            ]
          });

      var firstTournamentList, secondTournamentList, failure;
      service.getTournaments().then(function(_tournamentList_) {
        firstTournamentList = _tournamentList_;
      }).catch(function(err) {
        failure = {
          first_promise_rejected_with: err
        };
      });
      service.getTournaments().then(function(_tournamentList_) {
        secondTournamentList = _tournamentList_;
      }).catch(function(err) {
        failure = failure || {};
        failure.second_promise_rejected_with = err;
      });
      $httpBackend.flush(1);  // causes the first request to receive its response
      $rootScope.$apply();  // causes the promise to resolve

      expect(failure).toBeUndefined();
      expect(secondTournamentList).toBeDefined();
      expect(secondTournamentList).toBe(firstTournamentList);
    });
  });
});