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
   * The id of this pair.
   * @type {string}
   */
  this.pairId = '';

  /**
   * The players in this pair.
   * @type {tichu.TournamentPlayer[]}
   */
  this.players = [];
};


/**
 * Updates the pair id for a given TournamentPair.
 */
tichu.TournamentPair.prototype.setPairId = function setPairId(pairId) {
  this.pairId = pairId;
}

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
 * Holder for data for status of all hands in the tournament.
 * @constructor 
 */
tichu.TournamentStatus = function TournamentStatus() {
  this.roundStatus = [];
};


/**
 * Holder for data for status of all hands in a specific round.
 * @constructor
 */
tichu.RoundStatus = function RoundStatus() {
  this.roundNo = 0;
  this.unscoredHands = [];
  this.scoredHands = [];
}

/**
 * Holder for identifying a specific hand by participants, hand number, and table.
 * @constructor
 */
tichu.HandIdentifier = function HandIdentifier() {
  this.northSouthPair = 0;
  this.eastWestPair = 0;
  this.tableNo = 0;
  this.handNo = 0;
}

/**
 * Holder for all tracked changes to a specific hand.
 * @param {[tichu.Change]} changes list of changes associated with this hand.
 * @constructor 
 */
tichu.ChangeLog = function ChangeLog() {
  this.changes = [];
};

/**
 * Holder for one change to a hand score.
 * @param {tichu.HandScore} handScore score in this change
 * @param {number} changedBy pair that made this change. 0 for administrator.
 * @param {string} timestamp YYYY-DD-MM HH:MM formatted time string.
 * @constructor 
 */
tichu.Change = function Change(handScore, changedBy, timestamp) {
  this.handScore = handScore;
  this.changedBy = changedBy;
  this.timestamp = timestamp;
}


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
  /**
   * True if this tournament has scored hands (meaning that its number of boards and pairs may not be edited).
   * @type {boolean}
   */
  this.hasScoredHands = false;
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
 * A player request, used as part of a TournamentRequest.
 * @constructor
 */
tichu.PlayerRequest = function PlayerRequest() {
  /**
   * The number of the pair this player is part of.
   * @type {?number}
   */
  this.pairNo = null;
  /**
   * The name of this player.
   * @type {?string}
   */
  this.name = null;
  /**
   * The e-mail address of this player.
   * @type {?string}
   */
  this.email = null;
};

/** Converts the names of this PlayerRequest into the form the server expects. */
tichu.PlayerRequest.prototype.toJSON = function toJSON() {
  return {
    'pair_no': this.pairNo,
    'name': this.name || undefined,
    'email': this.email || undefined
  }
};

/**
 * A tournament request, used to create a tournament or edit one which has not been played.
 * @constructor
 */
tichu.TournamentRequest = function TournamentRequest() {
  /**
   * The title of the newly created tournament.
   * @type {?string}
   */
  this.name = null;
  /**
   * The number of pairs playing in this tournament.
   * @type {?number}
   */
  this.noPairs = null;
  /**
   * The number of boards to be played in this tournament.
   * @type {?number}
   */
  this.noBoards = null;
  /**
   * The set of player objects detailing the players in the pairs.
   * @type {tichu.PlayerRequest[]}
   */
  this.players = [];
};

/** Converts the names of this TournamentRequest into the form the server expects. */
tichu.TournamentRequest.prototype.toJSON = function toJSON() {
  return {
    'name': this.name,
    'no_pairs': this.noPairs,
    'no_boards': this.noBoards,
    'players': this.players
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
   * @type {number|string}
   */
  this.northSouthScore = 0;

  /**
   * The score earned by the east-west pair in this hand, including Tichu bonuses and penalties.
   * @type {number|string}
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
   * The names of the opponents.
   * @type {string}
   */
  this.opponentNames = [];

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