"use strict";
(function(angular) {
  /**
   * Main controller for the tournament edit page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {TichuTournamentService} TichuTournamentService
   * @param {$mdDialog} $mdDialog
   * @param {angular.$window} $window
   * @param {angular.$location} $location
   * @param {$route} $route
   * @param {!{failure: ?tichu.RpcError, id: ?string, tournament: ?tichu.Tournament}} loadResults
   * @ngInject
   */
  function TournamentFormController($scope, TichuTournamentService, $mdDialog, $window, $location, $route, loadResults) {
    var backPath = "/tournaments" + (loadResults.id ? "/" + loadResults.id + "/view" : "");
    $scope.appController.setPageHeader({
      header: loadResults.failure
          ? "Tournament Error"
          : (loadResults.tournament ? "Editing " + loadResults.tournament.name : "Create Tournament"),
      backPath: backPath,
      showHeader: true
    });

    /**
     * The tournament service injected at creation.
     * @type {TichuTournamentService}
     * @private
     */
    this._tournamentService = TichuTournamentService;

    /**
     * The original tournament being edited, if there was one.
     *
     * @type {tichu.Tournament}
     */
    this.original = loadResults.tournament;

    /**
     * The details about the failure, if there was one.
     *
     * @type {tichu.RpcError}
     */
    this.failure = loadResults.failure;

    /** The location service injected at creation. */
    this._$location = $location;

    /** The scope this controller exists in. */
    this._$scope = $scope;

    /**
     * The dialog service injected at creation.
     * @type {$mdDialog}
     * @private
     */
    this._$mdDialog = $mdDialog;

    /**
     * Whether this form is currently saving.
     *
     * @type {boolean}
     */
    this.saving = false;

    /**
     * The editable tournament object for the user to customize.
     * @type {tichu.TournamentRequest}
     */
    this.tournament = new tichu.TournamentRequest();

    if (this.original) {
      this.tournament.name = this.original.name;
      this.tournament.noBoards = this.original.noBoards;
      this.tournament.noPairs = this.original.noPairs;
      var players = this.tournament.players;
      this.original.pairs.forEach(function(pair) {
        pair.players.forEach(function(player) {
          var request = new tichu.PlayerRequest();
          request.pairNo = pair.pairNo;
          request.name = player.name;
          request.email = player.email;
          players.push(request);
        });
      });
    }

    /**
     * The presets available to play tournaments with.
     *
     * @type {[{noPairs: number, noBoards: number, noHands: number, noRounds: number]}
     */
    this.boardPresets = [
      {
        noPairs: 11,
        noBoards: 14,
        noHands: 2,
        noRounds: 7
      },
      {
        noPairs: 11,
        noBoards: 21,
        noHands: 3,
        noRounds: 7
      },
      {
        noPairs: 11,
        noBoards: 16,
        noHands: 2,
        noRounds: 6
      },
      {
        noPairs: 11,
        noBoards: 24,
        noHands: 3,
        noRounds: 6
      },
      {
        noPairs: 10,
        noBoards: 24,
        noHands: 3,
        noRounds: 7
      },
      {
        noPairs: 10,
        noBoards: 16,
        noHands: 2,
        noRounds: 7
      },
      {
        noPairs: 9,
        noBoards: 18,
        noHands: 2,
        noRounds: 8
      },
      {
        noPairs: 9,
        noBoards: 27,
        noHands: 3,
        noRounds: 8
      },
      {
        noPairs: 9,
        noBoards: 14,
        noHands: 2,
        noRounds: 7
      },
      {
        noPairs: 9,
        noBoards: 21,
        noHands: 3,
        noRounds: 7
      },
      {
        noPairs: 8,
        noBoards: 16,
        noHands: 2,
        noRounds: 6
      },
      {
        noPairs: 8,
        noBoards: 24,
        noHands: 3,
        noRounds: 6
      },
      {
        noPairs: 7,
        noBoards: 14,
        noHands: 2,
        noRounds: 7
      },
      {
        noPairs: 7,
        noBoards: 21,
        noHands: 3,
        noRounds: 7
      },
      {
        noPairs: 6,
        noBoards: 15,
        noHands: 3,
        noRounds: 5
      }
    ];

    if (this.failure) {
      var redirectToLogin = this.failure.redirectToLogin;
      var dialog = $mdDialog.confirm()
          .title(this.failure.error)
          .textContent(this.failure.detail);
      if (redirectToLogin) {
        dialog = dialog
            .ok("Log me in")
            .cancel("Never mind");
      } else {
        dialog = dialog
            .ok("Try again")
            .cancel("Never mind");
      }
      $mdDialog.show(dialog).then(function () {
        if (redirectToLogin) {
          // use $window.location since we're going out of the Angular app
          $window.location.href = '/api/login?then=' + encodeURIComponent($location.url())
        } else {
          $route.reload();
        }
      }, function (autoHidden) {
        if (!autoHidden) {
          $location.url(backPath);
        }
      });

      $scope.$on("$destroy", function () {
        $mdDialog.cancel(true);
      });
    }
  }

  /** Clears the number of boards if the number of pairs is currently set to a value for which it would be invalid. */
  TournamentFormController.prototype.checkNoBoards = function checkNoBoards() {
    var noBoards = this.tournament.noBoards;
    var noPairs = this.tournament.noPairs;
    var possibilities = this.boardPresets
        .filter(function (preset) { return preset.noPairs === noPairs; })
        .map(function (preset) { return preset.noBoards; });

    if (possibilities.indexOf(noBoards) === -1) {
      this.tournament.noBoards = null;
    }
  };

  /** Adds a player to the set of players. */
  TournamentFormController.prototype.addPlayer = function addPlayer() {
    var request = new tichu.PlayerRequest();
    this.tournament.players.push(request);
    var pairCounts = this.tournament.players
        .map(function (player) { return player.pairNo })
        .reduce(function (list, pairNo) { list[pairNo] = (list[pairNo] || 0) + 1; return list;}, []);
    for (var i = 1; i <= this.tournament.noPairs; i += 1) {
      if ((pairCounts[i] || 0) < 2) {
        request.pairNo = i;
        return;
      }
    }
  };

  /** Removes a player from the set of players. */
  TournamentFormController.prototype.removePlayer = function removePlayer(index) {
    this.tournament.players.splice(index, 1);
  };

  /** Saves the tournament being edited, disabling the form until save is complete. */
  TournamentFormController.prototype.save = function save() {
    if (this.saving) {
      return;
    }
    this.saving = true;

    var self = this;

    var promise = this.original
        ? this._tournamentService.editTournament(this.original.id, this.tournament)
        : this._tournamentService.createTournament(this.tournament);

    promise.then(function(result) {
      self._$location
          .path("/tournaments/" + encodeURIComponent(result.id) + "/view");
    }).catch(function(failure) {
      self.saving = false;
      var alert = self._$mdDialog.alert()
          .title(failure.error)
          .textContent(failure.detail)
          .ok("Try again");
      var dialogDestroyed = false;
      self._$mdDialog.show(alert).then(function() {
        dialogDestroyed = true;
      });
      self._$scope.$on("$destroy", function() {
        if (!dialogDestroyed) {
          self._$mdDialog.hide();
        }
      });
    });
  };

  /**
   * Gets the unique values of the given property in the objects in the array.
   */
  function uniqueProperties(array, property) {
    if (!array) {
      return array;
    }
    return array
        .map(function(item) {return item[property];})
        .filter(function(item, index, self) {return self.indexOf(item) === index});
  }

  /**
   * Asynchronously loads the requested tournament.
   *
   * @param {TichuTournamentService} tournamentService
   * @param {string} id
   * @return {!angular.$q.Promise<!{failure: ?tichu.RpcError, id: ?string, tournament: ?tichu.Tournament}>}
   */
  function loadTournament(tournamentService, id) {
    return tournamentService.getTournament(id, true).then(function(result) {
      return {
        id: id,
        tournament: result
      };
    }).catch(function(rejection) {
      return {
        id: id,
        failure: rejection
      };
    });
  }

  /**
   * Configures the routing provider to load the tournament list at its path.
   *
   * @param {!$routeProvider} $routeProvider
   * @ngInject
   */
  function mapRoute($routeProvider) {
    $routeProvider
        .when("/tournaments/new", {
          templateUrl: "src/tournaments/tournament-form.html",
          controller: "TournamentFormController",
          controllerAs: "tournamentFormController",
          resolve: {
            "loadResults": /** @ngInject */ function() {
              return {
                id: null,
                tournament: null,
                failure: null
              };
            }
          }
        })
        .when("/tournaments/:id/edit", {
          templateUrl: "src/tournaments/tournament-form.html",
          controller: "TournamentFormController",
          controllerAs: "tournamentFormController",
          resolve: {
            "loadResults": /** @ngInject */ function($route, TichuTournamentService) {
              return loadTournament(TichuTournamentService, $route.current.params["id"]);
            }
          }
        });
  }

  angular.module("tichu-tournament-form", ["ng", "ngRoute", "ngMaterial", "tichu-tournament-service"])
      .controller("TournamentFormController", TournamentFormController)
      .config(mapRoute)
      .filter("tichuUnique", function() {return uniqueProperties;});
})(angular);