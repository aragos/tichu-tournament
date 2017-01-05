"use strict";
describe("movement-service module", function() {
  var $httpBackend, $rootScope;

  beforeEach(module("tichu-movement-service", "tichu-tournament-service"));

  beforeEach(inject(function(_$httpBackend_, _$rootScope_) {
    $httpBackend = _$httpBackend_;
    $rootScope = _$rootScope_;
  }));

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation();
    $httpBackend.verifyNoOutstandingRequest();
  });

  describe("TichuMovementService", function() {
    var service;

    beforeEach(inject(function (TichuMovementService) {
      service = TichuMovementService;
    }));

    function runPromise(promise, options) {
      var result = {};
      promise.then(function(promiseResolvedWith) {
        result = {
          promise_resolved_with: promiseResolvedWith === undefined ? "(undefined)" : promiseResolvedWith,
          actual_result: promiseResolvedWith
        };
      }).catch(function(promiseFailedWith) {
        result = {
          promise_failed_with: promiseFailedWith === undefined ? "(undefined)" : promiseFailedWith,
          actual_result: promiseFailedWith
        };
      });
      if (options.flushHttp) {
        $httpBackend.flush();
      }
      $rootScope.$apply();
      if (options.expectSuccess) {
        expect(result.promise_failed_with).toBeUndefined();
        expect(result.promise_resolved_with).toBeDefined();
        return result.actual_result;
      } else if (options.expectFailure) {
        expect(result.promise_resolved_with).toBeUndefined();
        expect(result.promise_failed_with).toBeDefined();
        return result.actual_result;
      }
      return result.actual_result;
    }

    describe("getMovement", function() {
      it("uses the first two parameters as tournament ID and pair number", function() {
        $httpBackend.expectGET('/api/tournaments/999000/movement/5')
            .respond(200, "I actually don't care what you think");
        runPromise(service.getMovement("999000", 5), {flushHttp: true});
      });

      it("does not send the X-tichu-pair-code header if only two parameters are given", function() {
        $httpBackend.expectGET('/api/tournaments/123456/movement/10', undefined, function(headers) {
          return !headers.hasOwnProperty('X-tichu-pair-code');
        }).respond(200, "This doesn't have to parse");
        runPromise(service.getMovement("123456", 10), {flushHttp: true});
      });

      it("sends the X-tichu-pair-code header iff a third parameter is supplied", function() {
        $httpBackend.expectGET('/api/tournaments/8675309/movement/3', undefined, function(headers) {
          return headers['X-tichu-pair-code'] === "PARE";
        }).respond(200, "Whatever boo");
        runPromise(service.getMovement("8675309", 3, "PARE"), {flushHttp: true});
      });

      it("only calls the server once per tournament-ID/pair-number set even if a different code is set", function() {
        $httpBackend.expectGET('/api/tournaments/2348/movement/7')
            .respond(200, {
              "name": "tournamont",
              "players": [],
              "movement": []
            });
        runPromise(service.getMovement("2348", 7), {flushHttp: true, expectSuccess: true});
        runPromise(service.getMovement("2348", 7), {flushHttp: false, expectSuccess: true});
        runPromise(service.getMovement("2348", 7, "KODE"), {flushHttp: false, expectSuccess: true});
      });

      it("does not cache errors", function() {
        $httpBackend.expectGET('/api/tournaments/2348/movement/7')
            .respond(500, {
              "error": "you screwed up",
              "detail": "like really bad"
            });
        var firstResult = runPromise(service.getMovement("2348", 7), {flushHttp: true, expectFailure: true});
        $httpBackend.expectGET('/api/tournaments/2348/movement/7')
            .respond(200, {
              "name": "tournamont",
              "players": [],
              "movement": []
            });
        var secondResult = runPromise(service.getMovement("2348", 7), {flushHttp: true, expectSuccess: true});
      });

      it("resolves the promise with the movement on success", function() {
        $httpBackend.expectGET('/api/tournaments/6969/movement/6')
            .respond(200, {
              "name": "a tournament",
              "players": [
                {
                  "name": "The Firstest",
                  "email": "fairest@best.example"
                },
                {
                  "name": "The Worstest",
                  "email": "garbage@hotmail.example"
                }
              ],
              "movement": [{
                "round": 1,
                "position": "1E",
                "opponent": 9,
                "relay_table": true,
                "hands": [
                  {
                    "hand_no": 8,
                    "score": {
                      "calls": {
                        "north": "",
                        "east": "GT",
                        "west": "",
                        "south": ""
                      },
                      "ns_score": 50,
                      "ew_score": -150,
                      "notes": "I am a note"
                    }
                  },
                  {
                    "hand_no": 3,
                    "score": {
                      "calls": {},
                      "ns_score": 15,
                      "ew_score": 85
                    }
                  }
                ]
              }, {
                "round": 2,
                "position": "2N",
                "opponent": 7,
                "relay_table": false,
                "hands": [{"hand_no": 5}]
              }]
            });
        var result = runPromise(service.getMovement("6969", 6), {flushHttp: true, expectSuccess: true});
        expect(result.tournamentId.id).toBe("6969");
        expect(result.tournamentId.name).toBe("a tournament");
        expect(result.pair.pairNo).toBe(6);
        expect(result.pair.players.length).toBe(2);
        expect(result.pair.players[0].name).toBe("The Firstest");
        expect(result.pair.players[1].email).toBe("garbage@hotmail.example");
        expect(result.rounds.length).toBe(2);
        expect(result.rounds[0].roundNo).toBe(1);
        expect(result.rounds[0].table).toBe("1");
        expect(result.rounds[0].position).toBe(tichu.PairPosition.EAST_WEST);
        expect(result.rounds[0].opponent).toBe(9);
        expect(result.rounds[0].isRelayTable).toBe(true);
        expect(result.rounds[0].hands.length).toBe(2);
        expect(result.rounds[0].hands[0].score).toBeDefined();
        expect(result.rounds[0].hands[0].score.calls[0]).toEqual(
            {side: tichu.Position.EAST, call: tichu.Call.GRAND_TICHU});
        expect(result.rounds[0].hands[0].score.calls.length).toBe(1);
        expect(result.rounds[0].hands[0].score.northSouthScore).toBe(50);
        expect(result.rounds[0].hands[0].score.eastWestScore).toBe(-150);
        expect(result.rounds[0].hands[0].score.notes).toBe("I am a note");
        expect(result.rounds[0].hands[1].score.calls.length).toBe(0);
        expect(result.rounds[0].hands[1].score.notes).toBeNull();
      });

      it("rejects the promise in case of an error", function() {
        $httpBackend.expectGET('/api/tournaments/2348/movement/7')
            .respond(500, {
              "error": "HELP I'M TRAPPED IN A MOVEMENT FACTORY",
              "detail": "ALSO EVERYTHING IS ON FIRE AAAHH"
            });
        var result = runPromise(service.getMovement("2348", 7), {flushHttp: true, expectFailure: true});
        expect(result.redirectToLogin).toBe(false);
        expect(result.error).toBe("HELP I'M TRAPPED IN A MOVEMENT FACTORY");
        expect(result.detail).toBe("ALSO EVERYTHING IS ON FIRE AAAHH");
      });

      it("sets redirectToLogin on the rejection for a 401", function() {
        $httpBackend.expectGET('/api/tournaments/2348/movement/7')
            .respond(401, {
              "error": "log yo butt in",
              "detail": "seriously don't be ridic"
            });
        var result = runPromise(service.getMovement("2348", 7), {flushHttp: true, expectFailure: true});
        expect(result.redirectToLogin).toBe(true);
      });

      it("does not make a second call even if a request comes in while waiting for the server the first time", function() {
        $httpBackend.expectGET('/api/tournaments/6606/movement/6')
            .respond(200, {
              "name": "a tournament",
              "players": [],
              "movement": []
            });
        var firstPromise = service.getMovement("6606", 6);
        var secondPromise = service.getMovement("6606", 6);
        var firstResult = runPromise(firstPromise, {flushHttp: true, expectSuccess: true});
        var secondResult = runPromise(secondPromise, {flushHttp: false, expectSuccess: true});
        expect(secondResult).toBe(firstResult);
      });

      it("does make a second call if a request with a different code comes while waiting for the server", function() {
        $httpBackend.expectGET('/api/tournaments/6606/movement/6', function(headers) {
          return !headers.hasOwnProperty('X-tichu-pair-code');
        }).respond(200, {
          "name": "a tournament",
          "players": [],
          "movement": []
        });
        var firstPromise = service.getMovement("6606", 6);
        $httpBackend.expectGET('/api/tournaments/6606/movement/6', function(headers) {
          return headers['X-tichu-pair-code'] === "PARE";
        }).respond(200, {
          "name": "a tournament",
          "players": [],
          "movement": []
        });
        var secondPromise = service.getMovement("6606", 6, "PARE");
        var firstResult = runPromise(firstPromise, {flushHttp: true, expectSuccess: true});
        var secondResult = runPromise(secondPromise, {flushHttp: false, expectSuccess: true});
        expect(secondResult).toBe(firstResult);
      });

      it("reuses and updates the same Hand object for opposite sides of the same hand", function() {
        $httpBackend.expectGET('/api/tournaments/6969/movement/6')
            .respond(200, {
              "name": "a tournament",
              "players": [],
              "movement": [{
                "round": 1,
                "position": "1E",
                "opponent": 9,
                "relay_table": false,
                "hands": [{"hand_no": 8}, {"hand_no": 3}]
              }, {
                "round": 2,
                "position": "2E",
                "opponent": 7,
                "relay_table": true,
                "hands": [{"hand_no": 5}]
              }]
            });
        var firstResult = runPromise(service.getMovement("6969", 6), {flushHttp: true, expectSuccess: true});
        $httpBackend.expectGET('/api/tournaments/6969/movement/9')
            .respond(200, {
              "name": "a tournament",
              "players": [],
              "movement": [{
                "round": 1,
                "position": "1N",
                "opponent": 6,
                "relay_table": false,
                "hands": [{"hand_no": 8}, {"hand_no": 3}]
              }, {
                "round": 2,
                "position": "1N",
                "opponent": 1,
                "relay_table": true,
                "hands": [{"hand_no": 5}]
              }]
            });
        var secondResult = runPromise(service.getMovement("6969", 9), {flushHttp: true, expectSuccess: true});
        // same partners, same boards, different sides
        expect(secondResult.rounds[0].hands[0]).toBe(firstResult.rounds[0].hands[0]);
        expect(secondResult.rounds[0].hands[1]).toBe(firstResult.rounds[0].hands[1]);
        // different partners, same boards
        expect(secondResult.rounds[1].hands[0]).not.toBe(firstResult.rounds[1].hands[0]);
      });

      describe("tournament header caching", function() {
        var tournamentService;

        beforeEach(inject(function (TichuTournamentService) {
          tournamentService = TichuTournamentService;
        }));

        it("reuses and updates tournament headers from the tournament service", function() {
          $httpBackend.expectGET('/api/tournaments/444')
              .respond(200, {
                "name": "my twoirnament",
                "no_boards": 24,
                "no_pairs": 8,
                "players": [],
                "hands": []
              });
          var tournament = runPromise(tournamentService.getTournament("444"), {flushHttp: true, expectSuccess: true});
          $httpBackend.expectGET('/api/tournaments/444/movement/4')
              .respond(200, {
                "name": "My Tournament",
                "players": [],
                "movement": []
              });
          var movement = runPromise(service.getMovement("444", 4), {flushHttp: true, expectSuccess: true});
          expect(movement.tournamentId).toBe(tournament._header);
          expect(tournament.name).toBe("My Tournament");
        });

        it("has its tournament headers reused and updated by the tournament service", function() {
          $httpBackend.expectGET('/api/tournaments/444/movement/4')
              .respond(200, {
                "name": "My Tournament",
                "players": [],
                "movement": []
              });
          var movement = runPromise(service.getMovement("444", 4), {flushHttp: true, expectSuccess: true});
          $httpBackend.expectGET('/api/tournaments/444')
              .respond(200, {
                "name": "my twoirnament",
                "no_boards": 24,
                "no_pairs": 8,
                "players": [],
                "hands": []
              });
          var tournament = runPromise(tournamentService.getTournament("444"), {flushHttp: true, expectSuccess: true});
          expect(tournament._header).toBe(movement.tournamentId);
          expect(movement.tournamentId.name).toBe("my twoirnament");
        });

        it("reuses and updates pair objects from the tournament service", function() {
          $httpBackend.expectGET('/api/tournaments/444')
              .respond(200, {
                "name": "my twoirnament",
                "no_boards": 24,
                "no_pairs": 1,
                "players": [
                  {"pair_no": 1, "name": "definitely not the same player", "email": "stillnottelling@duh.example"}],
                "hands": []
              });
          var tournament = runPromise(tournamentService.getTournament("444"), {flushHttp: true, expectSuccess: true});
          $httpBackend.expectGET('/api/tournaments/444/movement/1')
              .respond(200, {
                "name": "My Tournament",
                "players": [{"name": "a player", "email": "whoaskedyou@shutup.example"}],
                "movement": []
              });
          var movement = runPromise(service.getMovement("444", 1), {flushHttp: true, expectSuccess: true});
          expect(tournament.pairs[0]).toBe(movement.pair);
          expect(tournament.pairs[0].players[0].name).toBe("a player");
          expect(tournament.pairs[0].players[0].email).toBe("whoaskedyou@shutup.example");
        });

        it("has its pair objects reused and updated by the tournament service", function() {
          $httpBackend.expectGET('/api/tournaments/444/movement/1')
              .respond(200, {
                "name": "My Tournament",
                "players": [{"name": "a player", "email": "whoaskedyou@shutup.example"}],
                "movement": []
              });
          var movement = runPromise(service.getMovement("444", 1), {flushHttp: true, expectSuccess: true});
          $httpBackend.expectGET('/api/tournaments/444')
              .respond(200, {
                "name": "my twoirnament",
                "no_boards": 24,
                "no_pairs": 1,
                "players": [
                    {"pair_no": 1, "name": "definitely not the same player", "email": "stillnottelling@duh.example"}],
                "hands": []
              });
          var tournament = runPromise(tournamentService.getTournament("444"), {flushHttp: true, expectSuccess: true});
          expect(tournament.pairs[0]).toBe(movement.pair);
          expect(movement.pair.players[0].name).toBe("definitely not the same player");
          expect(movement.pair.players[0].email).toBe("stillnottelling@duh.example");
        });
      });
    });
  });
});