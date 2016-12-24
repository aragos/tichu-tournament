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
 *     hands: !tichu.HandScore[]
 * }}
 */
tichu.Tournament;

/**
 * @typedef {{
 *     board_no: number,
 *     ns_pair: number,
 *     ew_pair: number,
 *     calls: (!tichu.Calls|!tichu.Call[]),
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
 *     side: string,
 *     call: string
 * }}
 */
tichu.Call;