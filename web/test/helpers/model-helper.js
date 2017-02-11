"use strict";

/**
 * Convenience function to create a PlayerRequest.
 * @param {{name: string=, email: string=, pairNo: number=}=} options
 * @returns {tichu.PlayerRequest}
 */
function makePlayerRequest(options) {
  options = options || {};
  var request = new tichu.PlayerRequest();
  request.name = options.name || "Player";
  request.email = options.email || "player@player.example";
  request.pairNo = options.pairNo || 1;
  return request;
}

/**
 * Convenience function to create a TournamentRequest.
 * @param {{name: string=, noBoards: number=, noPairs: number=, players: tichu.PlayerRequest[]=}=} options
 * @returns {tichu.TournamentRequest}
 */
function makeTournamentRequest(options) {
  options = options || {};
  var request = new tichu.TournamentRequest();
  request.name = options.name || "My New Tournament";
  request.noBoards = options.noBoards || 24;
  request.noPairs = options.noPairs || 8;
  request.players = options.players || [];
  return request;
}