"use strict";
describe("models", function() {
  function getJSON(value) {
    return JSON.parse(JSON.stringify(value));
  }

  describe("TournamentPair", function() {
    describe("setPlayers", function() {
      it("empties the player array if it receives an empty array", function() {
        var pair = new tichu.TournamentPair(5);
        pair.players.push(new tichu.TournamentPlayer());
        pair.players.push(new tichu.TournamentPlayer());
        pair.setPlayers([]);
        expect(pair.players.length).toBe(0);
      });
      it("reuses existing elements if any are present in order but trims down to the list size", function() {
        var pair = new tichu.TournamentPair(5);
        var originalPlayer = new tichu.TournamentPlayer();
        pair.players.push(originalPlayer);
        pair.players.push(new tichu.TournamentPlayer());
        pair.setPlayers([{name: "a player", email: "something@somewhere.example"}]);
        expect(pair.players.length).toBe(1);
        expect(pair.players[0]).toBe(originalPlayer);
      });
      it("updates values on existing elements and sets values on new elements", function() {
        var pair = new tichu.TournamentPair(5);
        pair.players.push(new tichu.TournamentPlayer());
        pair.setPlayers([
          {name: "a player", email: "something@somewhere.example"},
          {name: "a different player", email: "moredifferent@elsewhere.example"}
        ]);
        expect(pair.players[0].name).toBe("a player");
        expect(pair.players[0].email).toBe("something@somewhere.example");
        expect(pair.players[1].name).toBe("a different player");
        expect(pair.players[1].email).toBe("moredifferent@elsewhere.example");
      });
      it("adds new elements if the list was empty", function() {
        var pair = new tichu.TournamentPair(5);
        pair.setPlayers([
          {name: "a player", email: "something@somewhere.example"},
          {name: "a different player", email: "moredifferent@elsewhere.example"}
        ]);
        expect(pair.players.length).toBe(2);
      });
    });
  });
  describe("Tournament", function() {
    describe("setNoPairs", function() {
      it("empties the pair array if it receives 0", function() {
        var tournament = new tichu.Tournament(new tichu.TournamentHeader("12345"));
        tournament.pairs.push(new tichu.TournamentPair(1));
        tournament.pairs.push(new tichu.TournamentPair(2));
        tournament.pairs.push(new tichu.TournamentPair(3));
        tournament.setNoPairs(0, function() { throw new Error("factory was unexpectedly called"); });
        expect(tournament.pairs.length).toBe(0);
      });
      it("reuses existing elements if any are present in order but trims down to the new size", function() {
        var tournament = new tichu.Tournament(new tichu.TournamentHeader("12345"));
        var originalPair = new tichu.TournamentPair(1);
        tournament.pairs.push(originalPair);
        tournament.pairs.push(new tichu.TournamentPair(2));
        tournament.pairs.push(new tichu.TournamentPair(3));
        tournament.setNoPairs(1, function() { throw new Error("factory was unexpectedly called"); });
        expect(tournament.pairs.length).toBe(1);
        expect(tournament.pairs[0]).toBe(originalPair);
      });
      it("adds new elements by calling the factory if the list was empty or too small", function() {
        var tournament = new tichu.Tournament(new tichu.TournamentHeader("12345"));
        var factoryStore = [
            new tichu.TournamentPair(1),
            new tichu.TournamentPair(2),
            new tichu.TournamentPair(3)
        ];
        tournament.setNoPairs(3, function(pairNo) { return factoryStore[pairNo - 1] });
        expect(tournament.pairs.length).toBe(3);
        expect(tournament.pairs[0]).toBe(factoryStore[0]);
        expect(tournament.pairs[1]).toBe(factoryStore[1]);
        expect(tournament.pairs[2]).toBe(factoryStore[2]);
      });
    });
  });
  describe("HandScore", function() {
    describe("toJson", function() {
      it("forwards the northSouthScore to ns_score", function() {
        var score = new tichu.HandScore();
        score.northSouthScore = 100;
        expect(getJSON(score)["ns_score"]).toBe(100);
      });

      it("forwards the eastWestScore to ew_score", function() {
        var score = new tichu.HandScore();
        score.eastWestScore = 100;
        expect(getJSON(score)["ew_score"]).toBe(100);
      });

      it("forwards the notes to notes", function() {
        var score = new tichu.HandScore();
        score.notes = "something is very wrong here";
        expect(getJSON(score)["notes"]).toBe("something is very wrong here");
      });

      it("transforms an empty calls array into an empty calls object", function() {
        var score = new tichu.HandScore();
        expect(getJSON(score)["calls"]).toEqual({});
      });

      it("transforms elements in the call array into fields on the calls object", function() {
        var score = new tichu.HandScore();
        score.calls.push({side: tichu.Position.NORTH, call: tichu.Call.GRAND_TICHU});
        score.calls.push({side: tichu.Position.EAST, call: tichu.Call.TICHU});
        expect(getJSON(score)["calls"]).toEqual({"north": "GT", "east": "T"});
      });
    });
  });
  describe("PlayerRequest", function() {
    describe("toJSON", function() {
      it("translates camelcase to snakecase for pair_no", function() {
        var request = new tichu.PlayerRequest();
        request.name = "George III";
        request.email = "hailtothe@king.example";
        request.pairNo = 5;
        expect(getJSON(request)).toEqual({
          'pair_no': 5,
          'email': "hailtothe@king.example",
          'name': "George III"
        });
      });
      it("removes null or empty fields", function() {
        var request = new tichu.PlayerRequest();
        request.name = null;
        request.email = "";
        request.pairNo = 3;
        expect(getJSON(request)).toEqual({
          'pair_no': 3
        });
      });
    });
  });
  describe("TournamentRequest", function() {
    describe("toJSON", function() {
      it("translates camelcase to snakecase for no_boards/pairs", function() {
        var request = new tichu.TournamentRequest();
        request.name = "Tichu Jousting";
        request.noPairs = 10;
        request.noBoards = 11;
        var player = new tichu.PlayerRequest();
        player.pairNo = 9;
        player.name = "The Black Knight";
        request.players.push(player);
        expect(getJSON(request)).toEqual({
          name: "Tichu Jousting",
          no_pairs: 10,
          no_boards: 11,
          players: [
            {
              'pair_no': 9,
              'name': "The Black Knight"
            }
          ]
        });
      });
    });
  });
});