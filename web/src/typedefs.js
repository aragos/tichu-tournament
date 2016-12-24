"use strict";
/** @const */ var tichu = {};

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