"use strict";
describe("models", function() {
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
});