"use strict";
(function(angular) {
  /**
   * @typedef {{
   *   pair_no: number,
   *   name: string,
   *   email: string
   * }}
   */
  var FakePlayer;
  /**
   * @typedef {{
   *   id: string,
   *   name: string,
   *   no_pairs: number,
   *   no_boards: number,
   *   players: FakePlayer[]
   * }}
   */
  var FakeTournament;

  /**
   * In-memory backend service for testing code which uses the backend-speaking services.
   * @constructor
   * @ngInject
   * @name TichuFakeBackends
   * @param {ngMock.$httpBackend} $httpBackend
   */
  function TichuFakeBackends($httpBackend) {
    /**
     * The HTTP backend used to receive requests.
     * @type {ngMock.$httpBackend}
     * @private
     */
    this._$httpBackend = $httpBackend;
    /**
     * Whether the user should be considered logged in.
     * @type {boolean}
     */
    this.isLoggedIn = true;
    /**
     * Whether requests should fail with a 500 error.
     * @type {boolean}
     */
    this.requestCrash = false;
    /**
     * The list of existing tournaments.
     * @type {FakeTournament[]}
     */
    this.tournaments = [];
    /**
     * The next ID to be used for tournament creation.
     * @type {number}
     */
    this.nextTournamentId = 100000000;
  }

  /**
   * Installs handlers for all paths this fake backend handles.
   */
  TichuFakeBackends.prototype.install = function install() {
    this._$httpBackend.whenPOST("/api/tournaments").respond(this._handleCreateTournament.bind(this));
  };

  /**
   * Handler for creating a tournament.
   * @private
   * @param {string} method
   * @param {string} url
   * @param {*} data
   * @param {object} headers
   * @param {object} params
   * @returns {[number,*,object,string]}
   */
  TichuFakeBackends.prototype._handleCreateTournament = function createTournament(method, url, data, headers, params) {
    if (this.requestCrash) {
      return [500, {"error": "Crash", "detail": "The fake backend crashed as requested."}, {}, "Internal Server Error"];
    }
    if (!this.isLoggedIn) {
      return [
          401,
          {"error": "Not logged in", "detail": "The fake backend is configured to treat the user as logged out."},
          {},
          "Unauthorized"]
    }
    try {
      data = JSON.parse(data);
      ServiceHelpers.assertType("tournament request", data, "object", false);
      var inputPlayers = ServiceHelpers.assertType("players", data['players'], "array", true) || [];
      var players = inputPlayers.map(function(player, index) {
        return {
          pair_no: ServiceHelpers.assertType("player pair number " + index, player['pair_no'], "number", false),
          name: ServiceHelpers.assertType("player name " + index, player['name'], "string", false),
          email: ServiceHelpers.assertType("player email " + index, player['email'], "string", false)
        };
      });
      var tournament = {
        id: this.nextTournamentId.toString(),
        name: ServiceHelpers.assertType("tournament name", data['name'], "string", false),
        no_pairs: ServiceHelpers.assertType("number of pairs", data['no_pairs'], "number", false),
        no_boards: ServiceHelpers.assertType("number of boards", data['no_boards'], "number", false),
        players: players
      };
      this.nextTournamentId += 1;
      this.tournaments.push(tournament);
      return [200, {"id": tournament.id}, {}, "Created"];
    } catch (ex) {
      return [400, {"error": "Bad request", "detail": "Invalid request: " + ex.toString()}, {}, "Bad Request"]
    }
  };

  angular.module("tichu-fake-backends", ["ng", "ngMock"])
      .service("TichuFakeBackends", TichuFakeBackends);
})(angular);