"use strict";
(function(angular) {
  /**
   * Service to maintain a cache of movement-related model objects.
   *
   * @constructor
   * @name TichuMovementStore
   * @param {angular.$cacheFactory} $cacheFactory
   * @param {TichuTournamentStore} TichuTournamentStore
   * @ngInject
   */
  function TichuMovementStore($cacheFactory, TichuTournamentStore) {
    /**
     * The cache of Movement instances.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._movementCache = $cacheFactory("Movements");

    /**
     * The cache of Hand instances.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._handCache = $cacheFactory("Hands");

    /**
     * The cache of tournament-related objects.
     * @type {TichuTournamentStore}
     * @private
     */
    this._tournamentStore = TichuTournamentStore;
  }

  /**
   * Returns the cache key used to store the given movement.
   * @param {string} id The ID of the tournament this movement is from.
   * @param {number} pairNo The number of the pair this movement is for.
   * @private
   * @returns {string}
   */
  TichuMovementStore.prototype._getMovementCacheKey = function _getMovementCacheKey(id, pairNo) {
    return encodeURIComponent(id) + "/" + encodeURIComponent(pairNo.toString());
  };

  /**
   * Returns whether the given movement is stored in the cache.
   * @param {string} id The ID of the tournament this movement is from.
   * @param {number} pairNo The number of the pair this movement is for.
   * @returns {boolean}
   */
  TichuMovementStore.prototype.hasMovement = function hasMovement(id, pairNo) {
    return !!this._movementCache.get(this._getMovementCacheKey(id, pairNo));
  };

  /**
   * Retrieves a movement from the cache or creates one and adds it to the cache.
   * @param {string} id The ID of the tournament this movement is from.
   * @param {number} pairNo The number of the pair this movement is for.
   * @returns {tichu.Movement}
   */
  TichuMovementStore.prototype.getOrCreateMovement = function getOrCreateMovement(id, pairNo) {
    var cacheKey = this._getMovementCacheKey(id, pairNo);
    var movement = this._movementCache.get(cacheKey);
    if (!movement) {
      var tournamentHeader = this._tournamentStore.getOrCreateTournamentHeader(id);
      var pair = this._tournamentStore.getOrCreateTournamentPair(id, pairNo);
      movement = new tichu.Movement(tournamentHeader, pair);
      this._movementCache.put(cacheKey, movement);
    }
    return movement;
  };

  /**
   * Returns the cache key used to store the given hand.
   * @param {string} id The ID of the tournament this hand is from.
   * @param {number} nsPair The number of the north-south pair this hand is for.
   * @param {number} ewPair The number of the east-west pair this hand is for.
   * @param {number} handNo The number of the board played in this hand.
   * @private
   * @returns {string}
   */
  TichuMovementStore.prototype._getHandCacheKey = function _getHandCacheKey(id, nsPair, ewPair, handNo) {
    return encodeURIComponent(id)
        + "/" + encodeURIComponent(nsPair.toString())
        + "/" + encodeURIComponent(ewPair.toString())
        + "/" + encodeURIComponent(handNo.toString());
  };

  /**
   * Retrieves a hand from the cache or creates one and adds it to the cache.
   * @param {string} id The ID of the tournament this hand is from.
   * @param {number} nsPair The number of the north-south pair this hand is for.
   * @param {number} ewPair The number of the east-west pair this hand is for.
   * @param {number} handNo The number of the board played in this hand.
   * @returns {tichu.Hand}
   */
  TichuMovementStore.prototype.getOrCreateHand = function getOrCreateHand(id, nsPair, ewPair, handNo) {
    var cacheKey = this._getHandCacheKey(id, nsPair, ewPair, handNo);
    var hand = this._handCache.get(cacheKey);
    if (!hand) {
      hand = new tichu.Hand(nsPair, ewPair, handNo);
      this._handCache.put(cacheKey, hand);
    }
    return hand;
  };

  angular.module("tichu-movement-store", ["ng", "tichu-tournament-store"])
      .service("TichuMovementStore", TichuMovementStore);
})(angular);