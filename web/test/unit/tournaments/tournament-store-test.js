"use strict";
describe("tournament-store module", function() {
  beforeEach(module("tichu-tournament-store"));

  describe("TichuTournamentStore", function() {
    var store;

    beforeEach(inject(function (TichuTournamentStore) {
      store = TichuTournamentStore;
    }));

    describe("getTournamentHeader", function() {
      it("creates a new object if one wasn't in the cache", function() {
        var header = store.getOrCreateTournamentHeader("12345");
        expect(header.id).toBe("12345");
      });

      it("stores the object and returns it on subsequent calls", function() {
        var header = store.getOrCreateTournamentHeader("9999");
        expect(store.getOrCreateTournamentHeader("9999")).toBe(header);
      });

      it("returns different objects for different IDs", function() {
        var headerA = store.getOrCreateTournamentHeader("6969");
        var headerB = store.getOrCreateTournamentHeader("9696");
        expect(headerB).not.toBe(headerA);
      });
    });

    describe("getOrCreateTournamentPair", function() {
      it("creates a new object if one wasn't in the cache", function() {
        var pair = store.getOrCreateTournamentPair("12345", 1);
        expect(pair.pairNo).toBe(1);
      });

      it("stores the object and returns it on subsequent calls", function() {
        var pair = store.getOrCreateTournamentPair("12345", 3);
        expect(store.getOrCreateTournamentPair("12345", 3)).toBe(pair);
      });

      it("returns different objects for different IDs", function() {
        var pairA = store.getOrCreateTournamentPair("12345", 3);
        var pairB = store.getOrCreateTournamentPair("54321", 3);
        expect(pairB).not.toBe(pairA);
      });

      it("returns different objects for different pair numbers", function() {
        var pairA = store.getOrCreateTournamentPair("12345", 3);
        var pairB = store.getOrCreateTournamentPair("12345", 4);
        expect(pairB).not.toBe(pairA);
      });
    });
    
    describe("getOrCreateTournamentStatus", function() {
      it("creates a new object if one wasn't in the cache", function() {
        expect(store.hasTournamentStatus("12345")).toBe(false);
        var tournamentStatus = store.getOrCreateTournamentStatus("12345");
        expect(store.hasTournamentStatus("12345")).toBe(true);
      });

      it("stores the object and returns it on subsequent calls", function() {
        var tournamentStatus = store.getOrCreateTournamentStatus("9999");
        expect(store.getOrCreateTournamentStatus("9999")).toBe(tournamentStatus);
      });

      it("returns different objects for different IDs", function() {
        var tournamentStatusA = store.getOrCreateTournamentStatus("6969");
        var tournamentStatusB = store.getOrCreateTournamentStatus("9696");
        expect(tournamentStatusA).not.toBe(tournamentStatusB);
      });
    });

    describe("getOrCreateTournament", function() {
      it("creates a new object if one wasn't in the cache", function() {
        expect(store.hasTournament("12345")).toBe(false);
        var tournament = store.getOrCreateTournament("12345");
        expect(tournament.id).toBe("12345");
        expect(store.hasTournament("12345")).toBe(true);
      });

      it("stores the object and returns it on subsequent calls", function() {
        var tournament = store.getOrCreateTournament("9999");
        expect(store.getOrCreateTournament("9999")).toBe(tournament);
      });

      it("returns different objects for different IDs", function() {
        var tournamentA = store.getOrCreateTournament("6969");
        var tournamentB = store.getOrCreateTournament("9696");
        expect(tournamentB).not.toBe(tournamentA);
      });
    });
  });
});