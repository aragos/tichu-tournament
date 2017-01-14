"use strict";
/**
 * Namespace holding model types relevant to this app.
 * @const
 */
var tichu = {};

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
   * @type {?string}
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
 * Quickly updates the player list in the given TournamentPair, reusing TournamentPlayers if possible.
 * @param {{name:?string, email: ?string}[]} players The players to set in the list.
 */
tichu.TournamentPair.prototype.setPlayers = function setPlayers(players) {
  if (this.players.length > players.length) {
    this.players.splice(players.length);
  } else {
    while(this.players.length < players.length) {
      this.players.push(new tichu.TournamentPlayer());
    }
  }
  for (var i = 0; i < this.players.length; i += 1) {
    this.players[i].name = players[i].name;
    this.players[i].email = players[i].email;
  }
};

/**
 * The tournament object, containing the full details about the tournament and related objects.
 * @param {!tichu.TournamentHeader} header The header object this tournament is associated with.
 * @constructor
 */
tichu.Tournament = function Tournament(header) {
  /**
   * The header for this tournament, where its ID and name are actually stored.
   * @type {!tichu.TournamentHeader}
   * @private
   */
  this._header = header;
  /**
   * The number of boards played in this tournament.
   * @type {number}
   */
  this.noBoards = 0;
  /**
   * The pairs playing in this tournament.
   * @type {tichu.TournamentPair[]}
   */
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
  }
});

/**
 * Sets the number of pairs, populating the pairs array appropriately.
 * @param {number} noPairs The number of pairs to create.
 * @param {function(pairNo:number):tichu.TournamentPair} factory Factory used to populate the array.
 */
tichu.Tournament.prototype.setNoPairs = function setNoPairs(noPairs, factory) {
  if (!factory) {
    factory = function(pairNo) { return new tichu.TournamentPair(pairNo); }
  }
  if (this.pairs.length > noPairs) {
    this.pairs.splice(noPairs);
  } else {
    while(this.pairs.length < noPairs) {
      this.pairs.push(factory(this.pairs.length + 1));
    }
  }
};

/**
 * Enum for positions of pairs.
 * @enum {string}
 */
tichu.PairPosition = {
  NORTH_SOUTH: "N",
  EAST_WEST: "E"
};

/**
 * Checks if the value is a valid pair position.
 * @param {string} side The position to check against the enum.
 * @returns {boolean}
 */
tichu.isValidPairPosition = function isValidPairPosition(side) {
  return Object.keys(tichu.PairPosition).some(function(key) {
    return tichu.PairPosition[key] === side;
  });
};

/**
 * Enum for positions of individuals.
 * @enum {string}
 */
tichu.Position = {
  NORTH: "north",
  EAST: "east",
  WEST: "west",
  SOUTH: "south"
};

/**
 * Enum for calls, for recording in the score.
 * @enum {string}
 */
tichu.Call = {
  NO_CALL: "",
  TICHU: "T",
  GRAND_TICHU: "GT"
};

/**
 * Checks if the value is a valid call.
 * @param {string} call The position to check against the enum.
 * @returns {boolean}
 */
tichu.isValidCall = function isValidCall(call) {
  return Object.keys(tichu.Call).some(function(key) {
    return tichu.Call[key] === call;
  });
};

/**
 * Structure containing information about the score of a single hand.
 * @constructor
 */
tichu.HandScore = function HandScore() {
  /**
   * The list of calls in this hand, if there were any.
   * @type {{side: tichu.Position, call: tichu.Call}[]}
   */
  this.calls = [];

  /**
   * The score earned by the north-south pair in this hand, including Tichu bonuses and penalties.
   * @type {number}
   */
  this.northSouthScore = 0;

  /**
   * The score earned by the east-west pair in this hand, including Tichu bonuses and penalties.
   * @type {number}
   */
  this.eastWestScore = 0;

  /**
   * Notes recorded along with this hand's score, if any.
   * @type {?string}
   */
  this.notes = null;
};

/**
 * Returns an object representing this HandScore for purposes of JSON serialization.
 * @returns {Object}
 */
tichu.HandScore.prototype.toJSON = function toJSON() {
  var calls = {};
  this.calls.forEach(function (call) {
    calls[call.side] = call.call;
  });
  return {
    "ns_score": this.northSouthScore,
    "ew_score": this.eastWestScore,
    "notes": this.notes,
    "calls": calls
  }
};

/**
 * Structure containing information about a single hand, including its score (if any).
 * @constructor
 * @param {number} northSouthPair The north/south pair playing this hand.
 * @param {number} eastWestPair The east/west pair playing this hand.
 * @param {number} handNo The number of the hand.
 */
tichu.Hand = function Hand(northSouthPair, eastWestPair, handNo) {
  /**
   * The north/south pair playing this hand.
   * @type {number}
   */
  this.northSouthPair = northSouthPair;

  /**
   * The east/west pair playing this hand.
   * @type {number}
   */
  this.eastWestPair = eastWestPair;

  /**
   * The hand number, indicating the board that will be played.
   * @type {number}
   */
  this.handNo = handNo;

  /**
   * The score registered for this hand, if one has been registered.
   * @type {tichu.HandScore}
   */
  this.score = null;
};

/**
 * Structure containing information about a single round in the movement.
 * @constructor
 */
tichu.MovementRound = function MovementRound() {
  /**
   * The round number.
   * @type {number}
   */
  this.roundNo = 0;

  /**
   * Whether this round is a sit-out round, meaning the other properties are useless.
   * @type {boolean}
   */
  this.isSitOut = false;

  /**
   * The table number.
   * @type {string}
   */
  this.table = "";

  /**
   * Whether this round will be shared with another group playing the same hands.
   * @type {boolean}
   */
  this.isRelayTable = false;

  /**
   * The side to be played by the team this movement is for.
   * @type {tichu.PairPosition}
   */
  this.side = tichu.PairPosition.NORTH_SOUTH;

  /**
   * The opposing pair number.
   * @type {number}
   */
  this.opponent = 0;

  /**
   * The hands contained within this movement, including scores if applicable.
   * @type {tichu.Hand[]}
   */
  this.hands = [];
};

/**
 * Structure containing information about a movement.
 * @constructor
 * @param {!tichu.TournamentHeader} tournamentId
 * @param {!tichu.TournamentPair} pair
 */
tichu.Movement = function Movement(tournamentId, pair) {
  /**
   * The identifier of the tournament this movement is for.
   * @type {!tichu.TournamentHeader}
   */
  this.tournamentId = tournamentId;

  /**
   * The pair object holding information about the players this movement is for.
   * @type {!tichu.TournamentPair}
   */
  this.pair = pair;

  /**
   * The list of rounds contained within this movement.
   * @type {tichu.MovementRound[]}
   */
  this.rounds = [];
};

/**
 * Model for errors discovered in the process of contacting the server.
 * @constructor
 */
tichu.RpcError = function RpcError() {
  /**
   * Whether the error results from the user not being logged in.
   * @type {boolean}
   */
  this.redirectToLogin = false;
  /**
   * The main error text, containing a concise user-readable description of the problem.
   * @type {string}
   */
  this.error = "Server Error";
  /**
   * The error detail text, containing a more detailed user-readable description of the problem.
   * @type {string}
   */
  this.error = "An unexpected error occurred.";
};