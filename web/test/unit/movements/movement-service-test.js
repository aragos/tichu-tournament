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
    /** @type {PromiseHelper} */
    var runPromise;

    beforeEach(inject(function (TichuMovementService) {
      service = TichuMovementService;
      runPromise = promiseHelper($rootScope, $httpBackend);
    }));

    describe("getMovement", function() {
      it("uses the first two parameters as tournament ID and pair number", function() {
        $httpBackend.expectGET('/api/tournaments/999000/movement/5')
            .respond(200, "I actually don't care what you think");
        runPromise(service.getMovement("999000", 5), {flushHttp: true});
      });

      it("does not send the X-tichu-pair-code header if only two parameters are given", function() {
        $httpBackend.expectGET('/api/tournaments/123456/movement/10', function(headers) {
          return !headers.hasOwnProperty('X-tichu-pair-code');
        }).respond(200, "This doesn't have to parse");
        runPromise(service.getMovement("123456", 10), {flushHttp: true});
      });

      it("sends the X-tichu-pair-code header iff a third parameter is supplied", function() {
        $httpBackend.expectGET('/api/tournaments/8675309/movement/3', function(headers) {
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
                  },
                ],
                "opponent_names": ["Alpha", "Beta"]
              }, {
                "round": 2,
                "position": "2N",
                "opponent": 7,
                "relay_table": false,
                "hands": [{"hand_no": 5}],
                "opponent_names": []
              }, {
                "round": 3
              }]
            });
        var result = runPromise(service.getMovement("6969", 6), {flushHttp: true, expectSuccess: true});
        expect(result.tournamentId.id).toBe("6969");
        expect(result.tournamentId.name).toBe("a tournament");
        expect(result.pair.pairNo).toBe(6);
        expect(result.pair.players.length).toBe(2);
        expect(result.pair.players[0].name).toBe("The Firstest");
        expect(result.pair.players[1].email).toBe("garbage@hotmail.example");
        expect(result.rounds.length).toBe(3);
        expect(result.rounds[0].roundNo).toBe(1);
        expect(result.rounds[0].table).toBe("1");
        expect(result.rounds[0].position).toBe(tichu.PairPosition.EAST_WEST);
        expect(result.rounds[0].opponent).toBe(9);
        expect(result.rounds[0].isSitOut).toBe(false);
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
        expect(result.rounds[2].isSitOut).toBe(true);
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

      it("sets redirectToLogin on the rejection for a 403", function() {
        $httpBackend.expectGET('/api/tournaments/2348/movement/7')
            .respond(403, {
              "error": "nice try",
              "detail": "I know that's not the right code"
            });
        var result = runPromise(service.getMovement("2348", 7), {flushHttp: true, expectFailure: true});
        expect(result.redirectToLogin).toBe(true);
      });

      it("does not make a second call even if a request with refresh set comes in while waiting for the server the first time", function() {
        $httpBackend.expectGET('/api/tournaments/6606/movement/6')
            .respond(200, {
              "name": "a tournament",
              "players": [],
              "movement": []
            });
        var firstPromise = service.getMovement("6606", 6);
        var secondPromise = service.getMovement("6606", 6, null, true);
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

      it("does make a second call if a request with refresh comes after resolving", function() {
        $httpBackend.expectGET('/api/tournaments/6606/movement/6').respond(200, {
          "name": "a tournament",
          "players": [],
          "movement": []
        });
        var firstPromise = service.getMovement("6606", 6, null);
        var firstResult = runPromise(firstPromise, {flushHttp: true, expectSuccess: true});

        $httpBackend.expectGET('/api/tournaments/6606/movement/6').respond(200, {
          "name": "a different tournament",
          "players": [],
          "movement": []
        });
        var secondPromise = service.getMovement("6606", 6, null, true);
        var secondResult = runPromise(secondPromise, {flushHttp: true, expectSuccess: true});
        expect(secondResult).toBe(firstResult);
        expect(firstResult.tournamentId.name).toBe("a different tournament");
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
                "hands": [{"hand_no": 8}, {"hand_no": 3}],
                "opponent_names": ["Alpha", "Beta"]
              }, {
                "round": 2,
                "position": "2E",
                "opponent": 7,
                "relay_table": true,
                "hands": [{"hand_no": 5}],
                "opponent_names": ["Delta", "Gamma"]
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
                "hands": [{"hand_no": 8}, {"hand_no": 3}],
                "opponent_names": ["Alpha", "Beta"]
              }, {
                "round": 2,
                "position": "1N",
                "opponent": 1,
                "relay_table": true,
                "hands": [{"hand_no": 5}],
                "opponent_names": ["Delta", "Gamma"]
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
                "hands": [],
                "pair_ids": ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
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
                "hands": [],
                "pair_ids": ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
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
                "hands": [],
                "pair_ids": ["ABCD"]
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
                "pair_ids": ["ABCD"],
                "hands": []
              });
          var tournament = runPromise(tournamentService.getTournament("444"), {flushHttp: true, expectSuccess: true});
          expect(tournament.pairs[0]).toBe(movement.pair);
          expect(movement.pair.players[0].name).toBe("definitely not the same player");
          expect(movement.pair.players[0].email).toBe("stillnottelling@duh.example");
        });
      });
    });

    describe("recordScore", function() {
      var tournamentService;
      beforeEach(inject(function (TichuTournamentService) {
        tournamentService = TichuTournamentService;
        runPromise = promiseHelper($rootScope, $httpBackend);
      }));
      it("uses the first four parameters as tournament ID, pair numbers, and board", function() {
        $httpBackend.expectPUT('/api/tournaments/999000/hands/6/2/4')
            .respond(200, "");
        runPromise(service.recordScore("999000", 2, 4, 6, new tichu.HandScore()), {flushHttp: true});
      });

      it("does not send the X-tichu-pair-code header if only five parameters are given", function() {
        $httpBackend.expectPUT('/api/tournaments/123456/hands/1/7/3', undefined, function(headers) {
          return !headers.hasOwnProperty('X-tichu-pair-code');
        }).respond(200, "");
        runPromise(service.recordScore("123456", 7, 3, 1, new tichu.HandScore()), {flushHttp: true});
      });

      it("sends the X-tichu-pair-code header iff a sixth parameter is supplied", function() {
        $httpBackend.expectPUT('/api/tournaments/8675309/hands/8/3/6', undefined, function(headers) {
          return headers['X-tichu-pair-code'] === "PARE";
        }).respond(200, "");
        runPromise(
            service.recordScore("8675309", 3, 6, 8, new tichu.HandScore(), "PARE"),
            {flushHttp: true});
      });

      it("serializes the HandScore to JSON as the request body", function() {
        $httpBackend.expectPUT('/api/tournaments/1337/hands/2/2/2', {
          "calls": {
            "north": "T",
            "east": "GT"
          },
          "ns_score": 150,
          "ew_score": -150,
          "notes": "hahahahahaha what a fool"
        }).respond(200, "");
        var score = new tichu.HandScore();
        score.calls.push({side: tichu.Position.NORTH, call: tichu.Call.TICHU});
        score.calls.push({side: tichu.Position.EAST, call: tichu.Call.GRAND_TICHU});
        score.northSouthScore = 150;
        score.eastWestScore = -150;
        score.notes = "hahahahahaha what a fool";
        runPromise(
            service.recordScore("1337", 2, 2, 2, score),
            {flushHttp: true});
      });

      it("resolves the promise on success", function() {
        $httpBackend.expectPUT('/api/tournaments/123456/hands/6/2/4').respond(200, "");
        runPromise(
            service.recordScore("123456", 2, 4, 6, new tichu.HandScore()),
            {flushHttp: true, expectSuccess: true});
      });

      it("rejects the promise in case of an error", function() {
        $httpBackend.expectPUT('/api/tournaments/898989/hands/89/8/9')
            .respond(500, {
              "error": "your hand smells",
              "detail": "and your face smells too"
            });
        var result = runPromise(
            service.recordScore("898989", 8, 9, 89, new tichu.HandScore()),
            {flushHttp: true, expectFailure: true});
        expect(result.redirectToLogin).toBe(false);
        expect(result.error).toBe("your hand smells");
        expect(result.detail).toBe("and your face smells too");
      });

      it("sets redirectToLogin on the rejection for a 401", function() {
        $httpBackend.expectPUT('/api/tournaments/2348/hands/7/7/7')
            .respond(401, {
              "error": "log yo butt in",
              "detail": "seriously don't be ridic"
            });
        var result = runPromise(
            service.recordScore("2348", 7, 7, 7, new tichu.HandScore()),
            {flushHttp: true, expectFailure: true});
        expect(result.redirectToLogin).toBe(true);
      });

      it("sets redirectToLogin on the rejection for a 403", function() {
        $httpBackend.expectPUT('/api/tournaments/2348/hands/7/7/7')
            .respond(403, {
              "error": "log yo butt in",
              "detail": "seriously don't be ridic"
            });
        var result = runPromise(
            service.recordScore("2348", 7, 7, 7, new tichu.HandScore()),
            {flushHttp: true, expectFailure: true});
        expect(result.redirectToLogin).toBe(true);
      });

      it("sets the score on the shared hand in associated movements to the input on success", function() {
        $httpBackend.expectGET('/api/tournaments/6969/movement/9')
            .respond(200, {
              "name": "a tournament",
              "players": [],
              "movement": [{
                "round": 1,
                "position": "1E",
                "opponent": 6,
                "relay_table": false,
                "hands": [{"hand_no": 8}],
                "opponent_names": ["Alpha", "Beta"],
              }]
            });

        var movement = runPromise(
            service.getMovement("6969", 9),
            {flushHttp: true, expectSuccess:true});
        movement.rounds[0].hands[0].score = new tichu.HandScore();

        $httpBackend.expectPUT('/api/tournaments/6969/hands/8/6/9').respond(200, "");

        var handScore = new tichu.HandScore();
        var result = runPromise(
            service.recordScore("6969", 6, 9, 8, handScore),
            {flushHttp: true, expectSuccess: true});

        expect(movement.rounds[0].hands[0].score).toBe(handScore);
      });
      
      it("updates the tournaments status in the store on success", function() {
        $httpBackend.expectGET('/api/tournaments/6969/handStatus')
            .respond(200, {
              "rounds": [{
                "round": 2,
                "scored_hands": [],
                "unscored_hands": [{
                     "hand" : 8,
                     "ew_pair" : 9,
                     "ns_pair" : 6,
                     "table" : 12,
                 }]}]
            });
        var tournamentStatus = runPromise(tournamentService.getTournamentStatus("6969"),
                                          {flushHttp: true, expectSuccess:true})

        $httpBackend.expectPUT('/api/tournaments/6969/hands/8/6/9').respond(200, "");

        var handScore = new tichu.HandScore();
        var result = runPromise(
            service.recordScore("6969", 6, 9, 8, handScore),
            {flushHttp: true, expectSuccess: true});
        expect(tournamentStatus.roundStatus[0].scoredHands.length).toBe(1);
        expect(tournamentStatus.roundStatus[0].unscoredHands.length).toBe(0);
        expect(tournamentStatus.roundStatus[0].scoredHands[0].northSouthPair).toBe(6);
        expect(tournamentStatus.roundStatus[0].scoredHands[0].eastWestPair).toBe(9);
        expect(tournamentStatus.roundStatus[0].scoredHands[0].tableNo).toBe(12);
      });
      
      it("updates the tournaments status in the store on success, handles already scored hand", function() {
        $httpBackend.expectGET('/api/tournaments/6969/handStatus')
            .respond(200, {
              "rounds": [{
                "round": 2,
                "unscored_hands": [],
                "scored_hands": [{
                     "hand" : 8,
                     "ew_pair" : 9,
                     "ns_pair" : 6,
                     "table" : 12,
                 }]}]
            });
        var tournamentStatus = runPromise(tournamentService.getTournamentStatus("6969"),
                                          {flushHttp: true, expectSuccess:true})

        $httpBackend.expectPUT('/api/tournaments/6969/hands/8/6/9').respond(200, "");

        var handScore = new tichu.HandScore();
        var result = runPromise(
            service.recordScore("6969", 6, 9, 8, handScore),
            {flushHttp: true, expectSuccess: true});
        expect(tournamentStatus.roundStatus[0].scoredHands.length).toBe(1);
        expect(tournamentStatus.roundStatus[0].unscoredHands.length).toBe(0);
        expect(tournamentStatus.roundStatus[0].scoredHands[0].northSouthPair).toBe(6);
        expect(tournamentStatus.roundStatus[0].scoredHands[0].eastWestPair).toBe(9);
        expect(tournamentStatus.roundStatus[0].scoredHands[0].tableNo).toBe(12);
      });
      
      it("does not set the score on the shared hand in associated movements to the input on failure", function() {
        $httpBackend.expectGET('/api/tournaments/6969/movement/9')
            .respond(200, {
              "name": "a tournament",
              "players": [],
              "movement": [{
                "round": 1,
                "position": "1N",
                "opponent": 6,
                "relay_table": false,
                "hands": [{"hand_no": 8}],
                "opponent_names": ["Alpha", "Beta"]
              }]
            });

        var movement = runPromise(
            service.getMovement("6969", 9),
            {flushHttp: true, expectSuccess:true});
        var originalScore = new tichu.HandScore();
        movement.rounds[0].hands[0].score = originalScore;

        $httpBackend.expectPUT('/api/tournaments/6969/hands/8/6/9').respond(400, {
          error: "booo",
          detail: "your hand smells"
        });

        var handScore = new tichu.HandScore();
        runPromise(
            service.recordScore("6969", 6, 9, 8, handScore),
            {flushHttp: true, expectFailure: true});

        expect(movement.rounds[0].hands[0].score).toBe(originalScore);
      });
    });

    describe("clearScore", function() {
      var tournamentService;
      beforeEach(inject(function (TichuTournamentService) {
        tournamentService = TichuTournamentService;
        runPromise = promiseHelper($rootScope, $httpBackend);
      }));
      it("uses the first four parameters as tournament ID, pair numbers, and board", function() {
        $httpBackend.expectDELETE('/api/tournaments/999000/hands/6/2/4')
            .respond(200, "");
        runPromise(service.clearScore("999000", 2, 4, 6), {flushHttp: true});
      });

      it("does not send the X-tichu-pair-code header if only four parameters are given", function() {
        $httpBackend.expectDELETE('/api/tournaments/123456/hands/1/7/3', function(headers) {
          return !headers.hasOwnProperty('X-tichu-pair-code');
        }).respond(200, "");
        runPromise(service.clearScore("123456", 7, 3, 1), {flushHttp: true});
      });

      it("sends the X-tichu-pair-code header iff a fifth parameter is supplied", function() {
        $httpBackend.expectDELETE('/api/tournaments/8675309/hands/8/3/6', function(headers) {
          return headers['X-tichu-pair-code'] === "PARE";
        }).respond(200, "");
        runPromise(
            service.clearScore("8675309", 3, 6, 8, "PARE"),
            {flushHttp: true});
      });

      it("resolves the promise on success", function() {
        $httpBackend.expectDELETE('/api/tournaments/123456/hands/6/2/4').respond(200, "");
        runPromise(
            service.clearScore("123456", 2, 4, 6),
            {flushHttp: true, expectSuccess: true});
      });

      it("rejects the promise in case of an error", function() {
        $httpBackend.expectDELETE('/api/tournaments/898989/hands/89/8/9')
            .respond(500, {
              "error": "your hand smells",
              "detail": "and your face smells too"
            });
        var result = runPromise(
            service.clearScore("898989", 8, 9, 89),
            {flushHttp: true, expectFailure: true});
        expect(result.redirectToLogin).toBe(false);
        expect(result.error).toBe("your hand smells");
        expect(result.detail).toBe("and your face smells too");
      });

      it("sets redirectToLogin on the rejection for a 401", function() {
        $httpBackend.expectDELETE('/api/tournaments/2348/hands/7/7/7')
            .respond(401, {
              "error": "log yo butt in",
              "detail": "seriously don't be ridic"
            });
        var result = runPromise(
            service.clearScore("2348", 7, 7, 7),
            {flushHttp: true, expectFailure: true});
        expect(result.redirectToLogin).toBe(true);
      });

      it("sets redirectToLogin on the rejection for a 403", function() {
        $httpBackend.expectDELETE('/api/tournaments/2348/hands/7/7/7')
            .respond(403, {
              "error": "log yo butt in",
              "detail": "seriously don't be ridic"
            });
        var result = runPromise(
            service.clearScore("2348", 7, 7, 7),
            {flushHttp: true, expectFailure: true});
        expect(result.redirectToLogin).toBe(true);
      });

      it("clears the score on the shared hand in associated movements on success", function() {
        $httpBackend.expectGET('/api/tournaments/6969/movement/9')
            .respond(200, {
              "name": "a tournament",
              "players": [],
              "movement": [{
                "round": 1,
                "position": "1E",
                "opponent": 6,
                "relay_table": false,
                "hands": [{"hand_no": 8}],
                "opponent_names": ["Alpha", "Beta"]
              }],
            });

        var movement = runPromise(
            service.getMovement("6969", 9),
            {flushHttp: true, expectSuccess:true});
        movement.rounds[0].hands[0].score = new tichu.HandScore();

        $httpBackend.expectDELETE('/api/tournaments/6969/hands/8/6/9').respond(200, "");

        runPromise(
            service.clearScore("6969", 6, 9, 8),
            {flushHttp: true, expectSuccess: true});

        expect(movement.rounds[0].hands[0].score).toBeNull();
      });

      it("does not clear the score on the shared hand in associated movements on failure", function() {
        $httpBackend.expectGET('/api/tournaments/6969/movement/9')
            .respond(200, {
              "name": "a tournament",
              "players": [],
              "movement": [{
                "round": 1,
                "position": "1N",
                "opponent": 6,
                "relay_table": false,
                "hands": [{"hand_no": 8}],
                "opponent_names": ["Alpha", "Beta"]
              }]
            });

        var movement = runPromise(
            service.getMovement("6969", 9),
            {flushHttp: true, expectSuccess:true});
        var originalScore = new tichu.HandScore();
        movement.rounds[0].hands[0].score = originalScore;

        $httpBackend.expectDELETE('/api/tournaments/6969/hands/8/6/9').respond(400, {
          error: "booo",
          detail: "your hand smells"
        });

        runPromise(
            service.clearScore("6969", 6, 9, 8),
            {flushHttp: true, expectFailure: true});

        expect(movement.rounds[0].hands[0].score).toBe(originalScore);
      });
      
      it("updates the deleted tournaments status in the store on success", function() {
        $httpBackend.expectGET('/api/tournaments/6969/handStatus')
            .respond(200, {
              "rounds": [{
                "round": 2,
                "unscored_hands": [],
                "scored_hands": [{
                     "hand" : 8,
                     "ew_pair" : 9,
                     "ns_pair" : 6,
                     "table" : 12,
                 }]}]
            });
        var tournamentStatus = runPromise(tournamentService.getTournamentStatus("6969"),
                                          {flushHttp: true, expectSuccess:true})

        $httpBackend.expectDELETE('/api/tournaments/6969/hands/8/6/9').respond(200, "");

        var result = runPromise(service.clearScore("6969", 6, 9, 8),
                                {flushHttp: true, expectSuccess: true});
        expect(tournamentStatus.roundStatus[0].unscoredHands.length).toBe(1);
        expect(tournamentStatus.roundStatus[0].scoredHands.length).toBe(0);
        expect(tournamentStatus.roundStatus[0].unscoredHands[0].northSouthPair).toBe(6);
        expect(tournamentStatus.roundStatus[0].unscoredHands[0].eastWestPair).toBe(9);
        expect(tournamentStatus.roundStatus[0].unscoredHands[0].tableNo).toBe(12);
      });
    });
  });
});