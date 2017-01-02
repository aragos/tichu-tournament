"use strict";
(function(angular) {
  /**
   * Main controller for the tournament detail page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {{id: string, tournament: tichu.Tournament}} tournament
   * @ngInject
   */
  function TournamentDetailController($scope, tournament) {
    $scope.appController.setPageHeader({
      header: tournament.tournament.name,
      backPath: "/tournaments",
      showHeader: true
    });

    /**
     * The ID of the tournament being displayed to the user.
     *
     * @type {string}
     * @export
     */
    this.tournamentId = tournament.id;

    /**
     * The tournament being displayed to the user.
     *
     * @type {!tichu.Tournament}
     * @export
     */
    this.tournament = tournament.tournament;
  }

  /**
   * Asynchronously loads the list of tournaments.
   *
   * @param {!angular.$q} $q
   * @param {string} id
   * @return {!angular.$q.Promise<{id: string, tournament: tichu.Tournament}>}
   */
  function loadTournament($q, id) {
    return $q.when({
      "id": id,
      "tournament": {
      "name": "Tournament Name",
        "no_pairs": 8,
        "no_boards": 10,
        "players": [{
      "pair_no": 1,
      "name": "Michael the Magnificent",
      "email": "michael@michael.com"
    }],
        "hands": [{
      "board_no": 3,
      "ns_pair": 4,
      "ew_pair": 6,
      "calls": {
        "north": "T",
        "east": "GT",
        "west": "",
        "south": ""
      },
      "ns_score": 150,
      "ew_score": -150,
      "notes": "hahahahahaha what a fool"
    }]
    }
  });
  }

  /**
   * Composes a list of pair numbers from the number of pairs.
   *
   * @param {number} noPairs The number of pair numbers to produce
   * @returns {number[]}
   */
  function composePairList(noPairs) {
    var result = [];
    for (var pairNo = 1; pairNo <= noPairs; pairNo += 1) {
      result.push(pairNo);
    }
    return result;
  }

  /**
   * Configures the routing provider to load the tournament list at its path.
   *
   * @param {!$routeProvider} $routeProvider
   * @ngInject
   */
  function mapRoute($routeProvider) {
    $routeProvider
        .when("/tournaments/:id", {
          templateUrl: "src/tournaments/tournament-detail.html",
          controller: "TournamentDetailController",
          controllerAs: "tournamentDetailController",
          resolve: {
            "tournament": /** @ngInject */ function($q, $route) {
              return loadTournament($q, $route.current.params["id"]);
            }
          }
        });
  }

  angular.module("tichu-tournament-detail", ["ng", "ngRoute", "ngMaterial"])
      .controller("TournamentDetailController", TournamentDetailController)
      .config(mapRoute)
      .filter("tichuTournamentPairNoList", function() {
        return composePairList;
      });
})(angular);