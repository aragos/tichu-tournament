"use strict";
describe("tournament-service module", function() {
  var $httpBackend, $rootScope, /** @type {PromiseHelper} */ runPromise;

  beforeEach(module("tichu-tournament-service"));

  beforeEach(inject(function(_$httpBackend_, _$rootScope_) {
    $httpBackend = _$httpBackend_;
    $rootScope = _$rootScope_;
    runPromise = promiseHelper($rootScope, $httpBackend);
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

    describe("getTournaments", function() {
      it("downloads the tournament list on first call", function() {
        $httpBackend.expectGET('/api/tournaments')
            .respond(200, {
              "tournaments": [
                {"id": "123", "name": "My First Tournament"},
                {"id": "321", "name": "My Other Tournament"}
              ]
            });

        var tournamentList = runPromise(service.getTournaments(), {
          flushHttp: true,
          expectSuccess: true
        });
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

        var firstTournamentList = runPromise(service.getTournaments(), {expectSuccess: true, flushHttp: true});
        var secondTournamentList = runPromise(service.getTournaments(), {expectSuccess: true});
        $httpBackend.verifyNoOutstandingRequest();
        expect(secondTournamentList).toBe(firstTournamentList);
      });

      it("rejects the returned promise if an error is returned", function() {
        $httpBackend.expectGET('/api/tournaments')
            .respond(500, {
              "error": "something baaaad",
              "detail": "is happening in Oz"
            });

        var rejection = runPromise(service.getTournaments(), {expectFailure: true, flushHttp: true});

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

        var rejection = runPromise(service.getTournaments(), {expectFailure: true, flushHttp: true});
        expect(rejection.redirectToLogin).toBe(true);
      });

      it("doesn't cache error responses", function() {
        $httpBackend.expectGET('/api/tournaments')
            .respond(500, {
              "error": "something baaaad",
              "detail": "is happening in Oz"
            });

        runPromise(service.getTournaments(), {expectFailure: true, flushHttp: true});

        $httpBackend.expectGET('/api/tournaments')
            .respond(200, {
              "tournaments": [
                {"id": "123", "name": "My First Tournament"},
                {"id": "321", "name": "My Other Tournament"}
              ]
            });

        runPromise(service.getTournaments(), {expectSuccess: true, flushHttp: true});
      });

      it("only makes one server call even if another call comes in before it returns", function() {
        $httpBackend.expectGET('/api/tournaments')
            .respond(200, {
              "tournaments": [
                {"id": "123", "name": "My First Tournament"},
                {"id": "321", "name": "My Other Tournament"}
              ]
            });

        var firstPromise = service.getTournaments();
        var secondPromise = service.getTournaments();
        var firstTournamentList = runPromise(firstPromise, {expectSuccess: true, flushHttp: 1});
        var secondTournamentList = runPromise(secondPromise, {expectSuccess: true});

        expect(secondTournamentList).toBe(firstTournamentList);
      });
    });

    describe("getTournament", function() {
      it("downloads the tournament on first call to getTournament", function () {
        $httpBackend.expectGET('/api/tournaments/123456')
            .respond(200, {
              "name": "My Cool Tournament",
              "no_boards": 24,
              "no_pairs": 8,
              "players": [
                {"pair_no": 1, "name": "Player 1.1", "email": "player1-1@email.example"},
                {"pair_no": 1, "name": "Player 1.2", "email": "player1-2@email.example"},
                {"pair_no": 5, "name": "Player 5.1", "email": "player5-1@email.example"}
              ],
              "hands": [],
              pair_ids: ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
            });

        var tournament = runPromise(service.getTournament("123456"), {
          expectSuccess: true,
          flushHttp: true
        });

        expect(tournament.id).toEqual("123456");
        expect(tournament.name).toEqual("My Cool Tournament");
        expect(tournament.noBoards).toEqual(24);
        expect(tournament.pairs.length).toEqual(8);
        expect(tournament.pairs[0].pairNo).toEqual(1);
        expect(tournament.pairs[0].players.length).toEqual(2);
        expect(tournament.pairs[1].players.length).toEqual(0);
        expect(tournament.pairs[4].players.length).toEqual(1);
        expect(tournament.pairs[0].players[1].name).toEqual("Player 1.2");
        expect(tournament.pairs[4].players[0].email).toEqual("player5-1@email.example");
        expect(tournament.hasScoredHands).toEqual(false);
      });

      it("sets hasScoredHands based on the presence of a non-empty hands array", function() {
        $httpBackend.expectGET('/api/tournaments/123456')
            .respond(200, {
              "name": "My Cool Tournament",
              "no_boards": 24,
              "no_pairs": 8,
              "players": [
                {"pair_no": 1, "name": "Player 1.1", "email": "player1-1@email.example"},
                {"pair_no": 1, "name": "Player 1.2", "email": "player1-2@email.example"},
                {"pair_no": 5, "name": "Player 5.1", "email": "player5-1@email.example"}
              ],
              "hands": [{
                "board_no": 3,
                "ns_pair": 4,
                "ew_pair": 6,
                "calls": {
                  "north": "T",
                  "east": "GT",
                  "west": "",
                  "south": ""
                },
                "ns_score": 150,
                "ew_score": -150,
                "notes": "hahahahahaha what a fool"
              }],
              pair_ids: ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
            });

        var tournament = runPromise(service.getTournament("123456"), {
          expectSuccess: true,
          flushHttp: true
        });

        expect(tournament.id).toEqual("123456");
        expect(tournament.name).toEqual("My Cool Tournament");
        expect(tournament.noBoards).toEqual(24);
        expect(tournament.pairs.length).toEqual(8);
        expect(tournament.pairs[0].pairNo).toEqual(1);
        expect(tournament.pairs[0].players.length).toEqual(2);
        expect(tournament.pairs[1].players.length).toEqual(0);
        expect(tournament.pairs[4].players.length).toEqual(1);
        expect(tournament.pairs[0].players[1].name).toEqual("Player 1.2");
        expect(tournament.pairs[4].players[0].email).toEqual("player5-1@email.example");
        expect(tournament.hasScoredHands).toEqual(true);
      });

      it("returns the tournament without a server call on subsequent calls", function () {
        $httpBackend.expectGET('/api/tournaments/123456')
            .respond(200, {
              "name": "My Cool Tournament",
              "no_boards": 24,
              "no_pairs": 8,
              "players": [
                {"pair_no": 1, "name": "Player 1.1", "email": "player1-1@email.example"},
                {"pair_no": 1, "name": "Player 1.2", "email": "player1-2@email.example"},
                {"pair_no": 5, "name": "Player 5.1", "email": "player5-1@email.example"}
              ],
              "hands": [],
              pair_ids: ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
            });

        var firstTournament = runPromise(service.getTournament("123456"), {expectSuccess: true, flushHttp: true});
        var secondTournament = runPromise(service.getTournament("123456"), {expectSuccess: true});
        $httpBackend.verifyNoOutstandingRequest();

        expect(secondTournament).toBe(firstTournament);
      });

      it("rejects the returned promise if an error is returned", function () {
        $httpBackend.expectGET('/api/tournaments/123456')
            .respond(500, {
              "error": "something baaaad",
              "detail": "is happening in Oz"
            });

        var rejection = runPromise(service.getTournament("123456"), {expectFailure: true, flushHttp: true});

        expect(rejection.redirectToLogin).toBe(false);
        expect(rejection.error).toBe("something baaaad");
        expect(rejection.detail).toBe("is happening in Oz");
      });

      it("sets redirectToLogin on the rejection for a 401", function () {
        $httpBackend.expectGET('/api/tournaments/123456')
            .respond(401, {
              "error": "u not logged in",
              "detail": "get over to the login page"
            });

        var rejection = runPromise(service.getTournament("123456"), {expectFailure: true, flushHttp: true});

        expect(rejection.redirectToLogin).toBe(true);
      });

      it("doesn't cache error responses", function () {
        $httpBackend.expectGET('/api/tournaments/123456')
            .respond(500, {
              "error": "something baaaad",
              "detail": "is happening in Oz"
            });

        runPromise(service.getTournament("123456"), {expectFailure: true, flushHttp: true});

        $httpBackend.expectGET('/api/tournaments/123456')
            .respond(200, {
              "name": "My Cool Tournament",
              "no_boards": 24,
              "no_pairs": 8,
              "players": [
                {"pair_no": 1, "name": "Player 1.1", "email": "player1-1@email.example"},
                {"pair_no": 1, "name": "Player 1.2", "email": "player1-2@email.example"},
                {"pair_no": 5, "name": "Player 5.1", "email": "player5-1@email.example"}
              ],
              "hands": [],
              pair_ids: ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
            });

        runPromise(service.getTournament("123456"), {expectSuccess: true, flushHttp: true});
      });

      it("only makes one server call even if another call comes in before it returns", function () {
        $httpBackend.expectGET('/api/tournaments/123456')
            .respond(200, {
              "name": "My Cool Tournament",
              "no_boards": 24,
              "no_pairs": 8,
              "players": [
                {"pair_no": 1, "name": "Player 1.1", "email": "player1-1@email.example"},
                {"pair_no": 1, "name": "Player 1.2", "email": "player1-2@email.example"},
                {"pair_no": 5, "name": "Player 5.1", "email": "player5-1@email.example"}
              ],
              "hands": [],
              pair_ids: ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
            });

        var firstPromise = service.getTournament("123456");
        var secondPromise = service.getTournament("123456");
        var firstTournament = runPromise(firstPromise, {
          expectSuccess: true,
          flushHttp: 1
        });
        var secondTournament = runPromise(secondPromise, {
          expectSuccess: true
        });

        expect(secondTournament).toBe(firstTournament);
      });

      it("makes a second server call if another call with refresh comes in after it returns", function () {
        $httpBackend.expectGET('/api/tournaments/123456')
            .respond(200, {
              "name": "My Cool Tournament",
              "no_boards": 24,
              "no_pairs": 8,
              "players": [
                {"pair_no": 1, "name": "Player 1.1", "email": "player1-1@email.example"},
                {"pair_no": 1, "name": "Player 1.2", "email": "player1-2@email.example"},
                {"pair_no": 5, "name": "Player 5.1", "email": "player5-1@email.example"}
              ],
              "hands": [],
              pair_ids: ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
            });

        var firstTournament = runPromise(service.getTournament("123456"), {
          expectSuccess: true,
          flushHttp: true
        });

        $httpBackend.expectGET('/api/tournaments/123456')
            .respond(200, {
              "name": "My Cooler Tournament",
              "no_boards": 24,
              "no_pairs": 8,
              "players": [
                {"pair_no": 1, "name": "Player 1.1", "email": "player1-1@email.example"},
                {"pair_no": 1, "name": "Player 1.2", "email": "player1-2@email.example"},
                {"pair_no": 5, "name": "Player 5.1", "email": "player5-1@email.example"}
              ],
              "hands": [],
              pair_ids: ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
            });

        var secondTournament = runPromise(service.getTournament("123456", true), {
          expectSuccess: true,
          flushHttp: true
        });

        expect(secondTournament).toBe(firstTournament);
        expect(secondTournament.name).toBe("My Cooler Tournament");
      });

      it("only makes one server call even if another call with refresh comes in before it returns", function () {
        $httpBackend.expectGET('/api/tournaments/123456')
            .respond(200, {
              "name": "My Cool Tournament",
              "no_boards": 24,
              "no_pairs": 8,
              "players": [
                {"pair_no": 1, "name": "Player 1.1", "email": "player1-1@email.example"},
                {"pair_no": 1, "name": "Player 1.2", "email": "player1-2@email.example"},
                {"pair_no": 5, "name": "Player 5.1", "email": "player5-1@email.example"}
              ],
              "hands": [],
              pair_ids: ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
            });

        var firstPromise = service.getTournament("123456");
        var secondPromise = service.getTournament("123456", true);
        var firstTournament = runPromise(firstPromise, {
          expectSuccess: true,
          flushHttp: 1
        });
        var secondTournament = runPromise(secondPromise, {
          expectSuccess: true
        });

        expect(secondTournament).toBe(firstTournament);
      });

      it("updates its title when the tournament list is downloaded", function () {    
        $httpBackend.expectGET('/api/tournaments/123456')
            .respond(200, {
              "name": "My Cool Tournament",
              "no_boards": 24,
              "no_pairs": 8,
              "players": [
                {"pair_no": 1, "name": "Player 1.1", "email": "player1-1@email.example"},
                {"pair_no": 1, "name": "Player 1.2", "email": "player1-2@email.example"},
                {"pair_no": 5, "name": "Player 5.1", "email": "player5-1@email.example"}
              ],
              "hands": [],
              pair_ids: ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
            });
        var tournament = runPromise(service.getTournament("123456"), {expectSuccess: true, flushHttp: true});

        $httpBackend.expectGET('/api/tournaments')
            .respond(200, {
              "tournaments": [
                {"id": "123456", "name": "My First Tournament"}
              ]
            });
        runPromise(service.getTournaments(), {expectSuccess: true, flushHttp: true});

        expect(tournament.name).toBe("My First Tournament");
      });

      it("updates the matching title in the tournament list when it is downloaded", function () {
        $httpBackend.expectGET('/api/tournaments')
            .respond(200, {
              "tournaments": [
                {"id": "123456", "name": "My First Tournament"}
              ]
            });
        var tournamentList = runPromise(service.getTournaments(), {expectSuccess: true, flushHttp: true});

        $httpBackend.expectGET('/api/tournaments/123456')
            .respond(200, {
              "name": "My Cool Tournament",
              "no_boards": 24,
              "no_pairs": 8,
              "players": [
                {"pair_no": 1, "name": "Player 1.1", "email": "player1-1@email.example"},
                {"pair_no": 1, "name": "Player 1.2", "email": "player1-2@email.example"},
                {"pair_no": 5, "name": "Player 5.1", "email": "player5-1@email.example"}
              ],
              "hands": [],
              pair_ids: ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
            });
        runPromise(service.getTournament("123456"), {expectSuccess: true, flushHttp: true});

        expect(tournamentList[0].name).toBe("My Cool Tournament");
      });
    });

    describe("createTournament", function() {
      it("sends the JSONified tournament request to the server", function () {
          $httpBackend.expectPOST("/api/tournaments", {
              name: "Tichu of the Damned",
              no_boards: 24,
              no_pairs: 8,
              players: [
                  {
                      name: "Dracula",
                      email: "master@castlevania.example",
                      pair_no: 4
                  }
              ]
          }).respond(200, {});

          runPromise(service.createTournament(makeTournamentRequest({
            name: "Tichu of the Damned",
            noBoards: 24,
            noPairs: 8,
            players: [
                makePlayerRequest({
                  name: "Dracula",
                  email: "master@castlevania.example",
                  pairNo: 4
                })
            ]
          })), {flushHttp: true});
      });

      it("returns a Tournament object representing the created tournament on success", function() {
        $httpBackend.expectPOST("/api/tournaments").respond(200, {
          "id": "0912348"
        });
        $httpBackend.expectGET('/api/tournaments/0912348/pairids')
            .respond(200, {
              "pair_ids": ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
        });

        var tournament = runPromise(service.createTournament(makeTournamentRequest({
          name: "Tichu of the Damned",
          noBoards: 24,
          noPairs: 8,
          players: [
            makePlayerRequest({
              name: "Dracula",
              email: "master@castlevania.example",
              pairNo: 4
            })
          ]
        })), {expectSuccess: true, flushHttp: true});

        expect(tournament.id).toBe("0912348");
        expect(tournament.name).toBe("Tichu of the Damned");
        expect(tournament.noBoards).toBe(24);
        expect(tournament.noPairs).toBe(8);
        expect(tournament.pairs[3].players[0].name).toBe("Dracula");
        expect(tournament.pairs[3].players[0].email).toBe("master@castlevania.example");
      });

      it("rejects the returned promise if an error is returned", function() {
        $httpBackend.expectPOST("/api/tournaments").respond(400, {
          "error": "What kind of request is this",
          "detail": "What do you even want me to do with this"
        });

        var rejection = runPromise(
            service.createTournament(makeTournamentRequest({})), {expectFailure: true, flushHttp: true});

        expect(rejection.error).toBe("What kind of request is this");
        expect(rejection.detail).toBe("What do you even want me to do with this");
        expect(rejection.redirectToLogin).toBe(false);
      });

      it("sets redirectToLogin on the rejection for a 401", function() {
        $httpBackend.expectPOST("/api/tournaments").respond(401, {
          "error": "Log your dumb ass in",
          "detail": "How am I supposed to work with this"
        });

        var rejection = runPromise(
            service.createTournament(makeTournamentRequest({})), {expectFailure: true, flushHttp: true});

        expect(rejection.redirectToLogin).toBe(true);
      });

      it("adds its header to the tournament list cache on success if there was one", function() {
        $httpBackend.expectGET('/api/tournaments')
            .respond(200, {
              "tournaments": [
                {"id": "123", "name": "My First Tournament"},
                {"id": "321", "name": "My Other Tournament"}
              ]
            });

        var tournamentList = runPromise(service.getTournaments(), {
          flushHttp: true,
          expectSuccess: true
        });

        $httpBackend.expectPOST("/api/tournaments").respond(200, {
          "id": "231"
        });
        $httpBackend.expectGET('/api/tournaments/231/pairids')
            .respond(200, {
              "pair_ids": ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
        });
    
        var tournament = runPromise(service.createTournament(makeTournamentRequest({
          name: "Tichu of the Damned"
        })), {expectSuccess: true, flushHttp: true});

        expect(tournamentList).toContain(tournament._header);
      });

      it("does not create a tournament list cache if there was not one", function() {
        $httpBackend.expectPOST("/api/tournaments").respond(200, {
          "id": "231"
        });
        $httpBackend.expectGET('/api/tournaments/231/pairids')
            .respond(200, {
              "pair_ids": ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
        });

        var tournament = runPromise(service.createTournament(makeTournamentRequest({
          name: "Tichu of the Damned"
        })), {expectSuccess: true, flushHttp: true});

        $httpBackend.expectGET('/api/tournaments')
            .respond(200, {
              "tournaments": [
                {"id": "123", "name": "My First Tournament"},
                {"id": "321", "name": "My Other Tournament"}
              ]
            });

        var tournamentList = runPromise(service.getTournaments(), {
          flushHttp: true,
          expectSuccess: true
        });

        expect(tournamentList).not.toContain(tournament._header);
      });

      it("puts the tournament in the cache for getTournament on success", function() {
        $httpBackend.expectPOST("/api/tournaments").respond(200, {
          "id": "231"
        });
        $httpBackend.expectGET('/api/tournaments/231/pairids')
            .respond(200, {
              "pair_ids": ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
        });

        var createdTournament = runPromise(service.createTournament(makeTournamentRequest({
          name: "Tichu of the Damned"
        })), {expectSuccess: true, flushHttp: true});

        var gotTournament = runPromise(service.getTournament("231"), {expectSuccess: true});
        $httpBackend.verifyNoOutstandingRequest();
        expect(gotTournament).toBe(createdTournament);
      });
    });

    describe("editTournament", function() {
      it("sends the JSONified tournament request to the server", function () {
        $httpBackend.expectPUT("/api/tournaments/120839", {
          name: "Tichu of the Damned",
          no_boards: 24,
          no_pairs: 8,
          players: [
            {
              name: "Dracula",
              email: "master@castlevania.example",
              pair_no: 4
            }
          ]
        }).respond(201, "");

        runPromise(service.editTournament("120839", makeTournamentRequest({
          name: "Tichu of the Damned",
          noBoards: 24,
          noPairs: 8,
          players: [
            makePlayerRequest({
              name: "Dracula",
              email: "master@castlevania.example",
              pairNo: 4
            })
          ]
        })), {flushHttp: true});
      });

      it("updates and returns the cached Tournament object representing the modified tournament on success", function() {
        $httpBackend.expectGET("/api/tournaments/98021").respond(200, {
          name: "Tichu of the Darned",
          no_boards: 15,
          no_pairs: 6,
          players: [{
            pair_no: 3,
            name: "Alucard",
            email: "noone@castlevania.example"
          }],
          pair_ids: ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI"]
        });

        var originalTournament = runPromise(service.getTournament("98021"), {
          flushHttp: true,
          expectSuccess: true
        });

        $httpBackend.expectPUT("/api/tournaments/98021").respond(201, "");
        $httpBackend.expectGET('/api/tournaments/98021/pairids')
            .respond(200, {
              "pair_ids": ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
            });

        var tournament = runPromise(service.editTournament("98021", makeTournamentRequest({
          name: "Tichu of the Damned",
          noBoards: 24,
          noPairs: 8,
          players: [
            makePlayerRequest({
              name: "Dracula",
              email: "master@castlevania.example",
              pairNo: 4
            })
          ]
        })), {expectSuccess: true, flushHttp: true});

        expect(tournament).toBe(originalTournament);
        expect(tournament.id).toBe("98021");
        expect(tournament.name).toBe("Tichu of the Damned");
        expect(tournament.noBoards).toBe(24);
        expect(tournament.noPairs).toBe(8);
        expect(tournament.pairs[2].players.length).toBe(0);
        expect(tournament.pairs[3].players.length).toBe(1);
        expect(tournament.pairs[3].players[0].name).toBe("Dracula");
        expect(tournament.pairs[3].players[0].email).toBe("master@castlevania.example");
      });

      it("rejects the returned promise if an error is returned", function() {
        $httpBackend.expectPUT("/api/tournaments/76543").respond(400, {
          "error": "What kind of request is this",
          "detail": "What do you even want me to do with this"
        });

        var rejection = runPromise(
            service.editTournament("76543", makeTournamentRequest({})), {expectFailure: true, flushHttp: true});

        expect(rejection.error).toBe("What kind of request is this");
        expect(rejection.detail).toBe("What do you even want me to do with this");
        expect(rejection.redirectToLogin).toBe(false);
      });

      it("sets redirectToLogin on the rejection for a 401", function() {
        $httpBackend.expectPUT("/api/tournaments/76543").respond(401, {
          "error": "Log your dumb ass in",
          "detail": "How am I supposed to work with this"
        });

        var rejection = runPromise(
            service.editTournament("76543", makeTournamentRequest({})), {expectFailure: true, flushHttp: true});

        expect(rejection.redirectToLogin).toBe(true);
      });

      it("updates its header in the tournament list cache on success if there was one", function() {
        $httpBackend.expectGET('/api/tournaments')
            .respond(200, {
              "tournaments": [
                {"id": "123", "name": "My First Tournament"},
                {"id": "321", "name": "My Other Tournament"}
              ]
            });
        
        var tournamentList = runPromise(service.getTournaments(), {
          flushHttp: true,
          expectSuccess: true
        });

        $httpBackend.expectPUT("/api/tournaments/123").respond(201);
        $httpBackend.expectGET('/api/tournaments/123/pairids')
            .respond(200, {
              "pair_ids": ["ABCD", "BCDE", "CDEF", "DEFG", "EFGH", "FGHI", "GHIJ", "HIJK"]
            });

        runPromise(service.editTournament("123", makeTournamentRequest({
          name: "Tichu of the Damned"
        })), {expectSuccess: true, flushHttp: true});

        expect(tournamentList[0].name).toBe("Tichu of the Damned");
      });
    });
  });
});