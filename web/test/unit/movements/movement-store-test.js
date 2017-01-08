"use strict";
describe("movement-store module", function() {
  beforeEach(module("tichu-movement-store", "tichu-tournament-store"));

  describe("TichuMovementStore", function() {
    var store, tournamentStore;

    beforeEach(inject(function (TichuMovementStore, TichuTournamentStore) {
      store = TichuMovementStore;
      tournamentStore = TichuTournamentStore;
    }));

    describe("getOrCreateMovement", function() {
      it("creates a new movement with a pair and tournament from the tournament store", function() {
        expect(store.hasMovement("12345", 5)).toBe(false);
        var movement = store.getOrCreateMovement("12345", 5);
        expect(store.hasMovement("12345", 5)).toBe(true);
        expect(movement.tournamentId).toBe(tournamentStore.getOrCreateTournamentHeader("12345"));
        expect(movement.pair).toBe(tournamentStore.getOrCreateTournamentPair("12345", 5));
      });

      it("stores the movement and returns it on subsequent calls", function() {
        var movement = store.getOrCreateMovement("9999", 9);
        expect(store.getOrCreateMovement("9999", 9)).toBe(movement);
      });

      it("returns different objects for different IDs", function() {
        var movementA = store.getOrCreateMovement("54321", 5);
        var movementB = store.getOrCreateMovement("12345", 5);
        expect(movementB).not.toBe(movementA);
      });

      it("returns different objects for different pair numbers", function() {
        var movementA = store.getOrCreateMovement("54321", 8);
        var movementB = store.getOrCreateMovement("54321", 9);
        expect(movementB).not.toBe(movementA);
      });
    });

    describe("getOrCreateHand", function() {
      it("creates a new hand with the hand number and pairs given", function() {
        var hand = store.getOrCreateHand("12345", 1, 2, 3);
        expect(hand.northSouthPair).toBe(1);
        expect(hand.eastWestPair).toBe(2);
        expect(hand.handNo).toBe(3);
      });

      it("stores the movement and returns it on subsequent calls", function() {
        var hand = store.getOrCreateHand("9999", 8, 9, 5);
        expect(store.getOrCreateHand("9999", 8, 9, 5)).toBe(hand);
      });

      it("returns different objects for different IDs", function() {
        var handA = store.getOrCreateHand("696969", 6, 9, 6);
        var handB = store.getOrCreateHand("969696", 6, 9, 6);
        expect(handB).not.toBe(handA);
      });

      it("returns different objects for different north-south pair numbers", function() {
        var handA = store.getOrCreateHand("696969", 5, 9, 6);
        var handB = store.getOrCreateHand("696969", 6, 9, 6);
        expect(handB).not.toBe(handA);
      });

      it("returns different objects for different east-west pair numbers", function() {
        var handA = store.getOrCreateHand("696969", 6, 8, 6);
        var handB = store.getOrCreateHand("696969", 6, 9, 6);
        expect(handB).not.toBe(handA);
      });

      it("returns different objects for different board numbers", function() {
        var handA = store.getOrCreateHand("696969", 6, 9, 5);
        var handB = store.getOrCreateHand("696969", 6, 9, 6);
        expect(handB).not.toBe(handA);
      });
    });
  });
});