"use strict";
/** @const */ var tichu = {};

/**
 * Holder for the basics of tournament data, as received from the server when listing tournaments.
 * @constructor
 * @param {string} id The identifier used for this tournament.
 */
tichu.TournamentHeader = function TournamentHeader(id) {
  /**
   * The identifier of this tournament.
   * @type {string}
   * @export
   */
  this.id = id;
  /**
   * The name of this tournament.
   * @type {string}
   * @export
   */
  this.name = "Unnamed Tournament";
};

/**
 * Holder for data about a player in a tournament.
 * @constructor
 */
tichu.TournamentPlayer = function TournamentPlayer() {
  /**
   * The name of this player.
   * @type {string}
   */
  this.name = "Player";
  /**
   * The email of this player.
   * @type {?string}
   */
  this.email = null;
};

/**
 * Holder for data about a single pair.
 * @param {number} pairNo The 1-indexed number of the pair.
 * @constructor
 */
tichu.TournamentPair = function TournamentPair(pairNo) {
  /**
   * The number of this pair.
   * @type {number}
   */
  this.pairNo = pairNo;
  /**
   * The players in this pair.
   * @type {tichu.TournamentPlayer[]}
   */
  this.players = [];
};

/**
 * The tournament object, containing the full details about the tournament and related objects.
 * @param {!tichu.TournamentHeader} header The header object this tournament is associated with.
 * @constructor
 */
tichu.Tournament = function Tournament(header) {
  this._header = header;
  this.noBoards = 0;
  this.pairs = [];
};

Object.defineProperty(tichu.Tournament.prototype, "id", {
  enumerable: true,
  get: function getId() {
    return this._header.id;
  }
});

Object.defineProperty(tichu.Tournament.prototype, "name", {
  enumerable: true,
  get: function getName() {
    return this._header.name;
  },
  set: function setName(name) {
    this._header.name = name;
  }
});

Object.defineProperty(tichu.Tournament.prototype, "noPairs", {
  enumerable: true,
  get: function getNoPairs() {
    return this.pairs.length;
  },
  set: function setNoPairs(num) {
    if (num < 0 || num > 10 || Math.floor(num) !== num) {
      throw new Error("no_pairs must be an integer >= 0 and <= 10");
    }
    if (this.pairs.length > num) {
      this.pairs.splice(num);
    } else {
      while(this.pairs.length < num) {
        this.pairs.push(new tichu.TournamentPair(this.pairs.length + 1));
      }
    }
  }
});

/**
 * @typedef {{
 *     id: string,
 *     name: string
 * }}
 */
tichu.TournamentSummary;

/**
 * @typedef {{
 *     id: string,
 *     name: string,
 *     noPairs: number,
 *     noBoards: number,
 *     hands: !tichu.HandScore[],
 *     players: (!tichu.Player[]|undefined)
 * }}
 */
tichu.Tournament;

/**
 * @typedef {{
 *     board_no: number,
 *     ns_pair: number,
 *     ew_pair: number,
 *     calls: !tichu.Calls,
 *     ns_score: (number|string),
 *     ew_score: (number|string),
 *     notes: string
 * }}
 */
tichu.HandScore;

/**
 * @typedef {{
 *     north: (string|undefined),
 *     east: (string|undefined),
 *     west: (string|undefined),
 *     south: (string|undefined)
 * }}
 */
tichu.Calls;

/**
 * @typedef {{
 *     pair_no: number,
 *     name: string,
 *     email: string
 * }}
 */
tichu.Player;

/**
 * @typedef {{
 *     name: string,
 *     email: string
 * }}
 */
tichu.PairPlayer;

/**
 * @typedef {{
 *     round: number,
 *     position: string,
 *     opponent: number,
 *     hands: number[],
 *     relay_table: boolean,
 *     score: !tichu.HandScore
 * }}
 */
tichu.MovementRound;

/**
 * @typedef {{
 *     name: string,
 *     players: !tichu.PairPlayer[],
 *     movement: !tichu.MovementRound[]
 * }}
 */
tichu.Movement;