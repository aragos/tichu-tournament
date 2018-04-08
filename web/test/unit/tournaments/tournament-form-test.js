"use strict";
describe("tichu-tournament-form module", function() {
  beforeEach(module("tichu-tournament-form", "tichu-fake-backends"));

  describe("TournamentFormController controller", function() {
    var scope;
    var $rootScope;
    var header;
    var $controller;
    var $route;
    var $mdDialog;
    var $location;
    var $window;
    var dialogDeferred;
    /** @type {TichuFakeBackends} */
    var fakeBackends;
    var $httpBackend;
    /** @type {TichuTournamentService} */
    var tournamentService;

    beforeEach(module(function($provide) {
      $window = {location: {href: "/tournaments/new"}};
      $provide.value("$window", $window);
    }));

    beforeEach(inject(function(/** angular.Scope */ _$rootScope_,
                               /** angular.$q */ $q,
                               /** angular.$controller */ _$controller_,
                               /** $route */ _$route_,
                               /** angular.$location */ _$location_,
                               /** TichuFakeBackends */ TichuFakeBackends,
                               /** TichuTournamentService */ TichuTournamentService,
                               /** ngMock.$httpBackend */ _$httpBackend_,
                               /** $mdDialog */ _$mdDialog_) {
      $rootScope = _$rootScope_;
      var appScope = $rootScope.$new(false);
      appScope.appController = {
        setPageHeader: function(_header_) {
          header = _header_;
        }
      };
      scope = appScope.$new(false);
      $controller = _$controller_;
      $route = _$route_;
      $location = _$location_;
      $mdDialog = _$mdDialog_;
      fakeBackends = TichuFakeBackends;
      tournamentService = TichuTournamentService;
      $httpBackend = _$httpBackend_;
      spyOn($route, "reload");
      spyOn($mdDialog, "show").and.callFake(function (presets) {
        dialogDeferred = $q.defer();
        return dialogDeferred.promise;
      });
      spyOn($mdDialog, "hide").and.callFake(function (result) {
        dialogDeferred.resolve(result);
      });
      spyOn($mdDialog, "cancel").and.callFake(function (result) {
        dialogDeferred.reject(result);
      })
    }));

    /**
     * Starts up the controller with the given load results.
     *
     * @param {Object=} results
     * @returns {TournamentFormController}
     */
    function loadController(results) {
      return $controller("TournamentFormController as tournamentFormController", {
        "$scope": scope,
        "loadResults": results || {
          id: null,
          failure: null,
          tournament: null
        }
      });
    }

    describe("checkNoBoards", function() {
      it("clears tournament.noBoards if noPairs is not set", function() {
        var tournamentFormController = loadController();

        tournamentFormController.boardPresets = [{noPairs:5, noBoards: 15, noHands: 3, noRounds: 5}];
        tournamentFormController.tournament.noPairs = null;
        tournamentFormController.tournament.noBoards = 15;

        tournamentFormController.checkNoBoards();

        expect(tournamentFormController.tournament.noBoards).toBeNull();
      });

      it("allows tournament.noBoards to remain the same if noPairs is set to a value which is valid for it", function() {
        var tournamentFormController = loadController();

        tournamentFormController.boardPresets = [{noPairs:5, noBoards: 15, noHands: 3, noRounds: 5}];
        tournamentFormController.tournament.noPairs = 5;
        tournamentFormController.tournament.noBoards = 15;

        tournamentFormController.checkNoBoards();

        expect(tournamentFormController.tournament.noBoards).toBe(15);
      });

      it("clears tournament.noBoards if noPairs is set to a value which has no configuration with a matching noBoards", function() {
        var tournamentFormController = loadController();

        tournamentFormController.boardPresets = [{noPairs:6, noBoards: 18, noHands: 3, noRounds: 6}];
        tournamentFormController.tournament.noPairs = 6;
        tournamentFormController.tournament.noBoards = 15;

        tournamentFormController.checkNoBoards();

        expect(tournamentFormController.tournament.noBoards).toBeNull();
      });
    });

    describe("addPlayer", function() {
      it("adds a new player to the end of the tournament.players list with a default pair number of 1", function() {
        var tournamentFormController = loadController();

        tournamentFormController.tournament.noPairs = 3;
        var existingPlayer = makePlayerRequest({pairNo: 1});
        tournamentFormController.tournament.players.push(existingPlayer);

        tournamentFormController.addPlayer();

        var resultList = tournamentFormController.tournament.players;
        expect(resultList.length).toBe(2);
        expect(resultList[0]).toBe(existingPlayer);
        expect(resultList[1]).not.toBe(existingPlayer);
        expect(resultList[1].pairNo).toBe(1);
      });

      it("uses the next pair number with less than 2 players in it", function() {
        var tournamentFormController = loadController();

        tournamentFormController.tournament.noPairs = 3;
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 1}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 1}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 2}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 2}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 3}));

        tournamentFormController.addPlayer();

        var resultList = tournamentFormController.tournament.players;
        expect(resultList[5].pairNo).toBe(3);
      });

      it("will create a lower pair number than the current max if one is open", function() {
        var tournamentFormController = loadController();

        tournamentFormController.tournament.noPairs = 3;
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 1}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 1}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 1}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 2}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 3}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 3}));

        tournamentFormController.addPlayer();

        var resultList = tournamentFormController.tournament.players;
        expect(resultList[6].pairNo).toBe(2);
      });

      it("adds a player with an unset pair number if all pairs have 2 or more players", function() {
        var tournamentFormController = loadController();

        tournamentFormController.tournament.noPairs = 3;
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 1}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 1}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 2}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 2}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 3}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 3}));

        tournamentFormController.addPlayer();

        var resultList = tournamentFormController.tournament.players;
        expect(resultList[6].pairNo).toBeNull();
      });
    });

    describe("removePlayer", function() {
      it("removes the given player from the tournament.players list", function() {
        var tournamentFormController = loadController();

        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 1}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 2}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 3}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 4}));
        tournamentFormController.tournament.players.push(makePlayerRequest({pairNo: 5}));

        tournamentFormController.removePlayer(2);

        var resultList = tournamentFormController.tournament.players;
        expect(resultList.length).toBe(4);
        expect(resultList.map(function(request) { return request.pairNo })).toEqual([1, 2, 4, 5]);
      });
    });

    describe("in create mode", function() {
      it("sets a header", function() {
        loadController({
          id: null,
          failure: null,
          tournament: null
        });
        expect(header.header).toBe("Create Tournament");
        expect(header.backPath).toBe("/tournaments");
        expect(header.showHeader).toBe(true);
      });

      it("creates an empty TournamentRequest", function() {
        var tournamentFormController = loadController({
          id: null,
          failure: null,
          tournament: null
        });
        expect(tournamentFormController.tournament.name).toBeNull();
        expect(tournamentFormController.tournament.noPairs).toBeNull();
        expect(tournamentFormController.tournament.noBoards).toBeNull();
        expect(tournamentFormController.tournament.players).toEqual([]);
      });

      it("stores null in the original field", function() {
        var tournamentFormController = loadController({
          id: null,
          failure: null,
          tournament: null
        });
        expect(tournamentFormController.original).toBeNull();
      });

      it("displays a dialog and sets the failure in case of error", function() {
        var tournamentFormController = loadController({
          id: null,
          tournament: null,
          failure: {
            redirectToLogin: false,
            error: "An error happened",
            detail: "It was a very erroneous error"
          }
        });
        expect(tournamentFormController.failure).toBeTruthy();
        expect($mdDialog.show).toHaveBeenCalled();
      });

      it("reloads the page when the dialog is OK'd", function() {
        loadController({
          id: null,
          tournament: null,
          failure: {
            redirectToLogin: false,
            error: "An error happened",
            detail: "It was a very erroneous error"
          }
        });
        dialogDeferred.resolve();
        $rootScope.$apply();
        expect($route.reload).toHaveBeenCalled();
      });

      it("leaves for /tournaments when the dialog is canceled", function() {
        $location.url("/tournaments/new");
        loadController({
          id: null,
          tournament: null,
          failure: {
            redirectToLogin: false,
            error: "An error happened",
            detail: "It was a very erroneous error"
          }
        });
        dialogDeferred.reject();
        $rootScope.$apply();
        expect($location.url()).toBe("/tournaments");
      });

      it("opens the login page when the dialog is OK'd on a login error", function() {
        $window.location.href = "/tournaments/new";
        $location.url("/tournaments/new");
        loadController({
          id: null,
          tournament: null,
          failure: {
            redirectToLogin: true,
            error: "Log in already",
            detail: "What are you even doing here"
          }
        });
        dialogDeferred.resolve();
        $rootScope.$apply();
        expect($window.location.href).toBe("/api/login?then=%2Ftournaments%2Fnew");
      });

      it("cancels the dialog and doesn't change URLs when the scope is destroyed", function() {
        $location.url("/tournaments/new");
        loadController({
          failure: {
            redirectToLogin: false,
            error: "An error happened",
            detail: "It was a very erroneous error"
          }
        });
        scope.$destroy();
        expect($mdDialog.cancel).toHaveBeenCalled();
        $rootScope.$apply();
        expect($location.url()).toBe("/tournaments/new");
      });

      describe("save", function() {
        beforeEach(function() {
          fakeBackends.install();
        });

        afterEach(function() {
          $httpBackend.verifyNoOutstandingExpectation();
          $httpBackend.verifyNoOutstandingRequest();
        });

        it("starts off not saving", function() {
          var tournamentFormController = loadController({
            id: null,
            failure: null,
            tournament: null
          });
          expect(tournamentFormController.saving).toBe(false);
        });

        it("sets the saving member to true", function() {
          var tournamentFormController = loadController({
            id: null,
            tournament: null,
            failure: null
          });

          tournamentFormController.save();

          expect(tournamentFormController.saving).toBe(true);
          $httpBackend.flush();
        });

        it("only saves once even if called multiple times", function() {
          var tournamentFormController = loadController({
            id: null,
            tournament: null,
            failure: null
          });

          spyOn(tournamentService, "createTournament").and.callThrough();

          tournamentFormController.save();
          tournamentFormController.save();

          expect(tournamentService.createTournament.calls.count()).toBe(1);
          $httpBackend.flush();
        });

        it("calls createTournament with the tournament member", function() {
          var tournamentFormController = loadController({
            id: null,
            tournament: null,
            failure: null
          });

          tournamentFormController.tournament = makeTournamentRequest({
            name: "My Cool Tournament",
            noPairs: 5,
            noBoards: 15,
            players: [
              makePlayerRequest({
                pairNo: 3,
                name: "A Player",
                email: "aplayer@tichu.example"
              })
            ]
          });

          tournamentFormController.save();

          $httpBackend.flush();
          $rootScope.$apply();

          expect(fakeBackends.tournaments.length).toBe(1);
          expect(fakeBackends.tournaments[0].name).toBe("My Cool Tournament");
          expect(fakeBackends.tournaments[0].no_pairs).toBe(5);
          expect(fakeBackends.tournaments[0].no_boards).toBe(15);
          expect(fakeBackends.tournaments[0].players.length).toBe(1);
          expect(fakeBackends.tournaments[0].players[0].name).toBe("A Player");
          expect(fakeBackends.tournaments[0].players[0].email).toBe("aplayer@tichu.example");
          expect(fakeBackends.tournaments[0].players[0].pair_no).toBe(3);
        });

        it("displays a dialog and exits saving mode if the save fails", function() {
          var tournamentFormController = loadController({
            id: null,
            tournament: null,
            failure: null
          });

          tournamentFormController.tournament = makeTournamentRequest();
          fakeBackends.requestCrash = true;

          tournamentFormController.save();

          $httpBackend.flush();
          $rootScope.$apply();

          expect($mdDialog.show).toHaveBeenCalled();
          expect(tournamentFormController.saving).toBe(false);
        });

        it("redirects to the new tournament's view page on success", function() {
          $location.url("/tournaments/new");
          var tournamentFormController = loadController({
            id: null,
            tournament: null,
            failure: null
          });

          tournamentFormController.tournament = makeTournamentRequest();
          fakeBackends.nextTournamentId = 12345678;

          tournamentFormController.save();

          $httpBackend.flush();
          $rootScope.$apply();

          expect($mdDialog.show).not.toHaveBeenCalled();
          expect($location.url()).toBe("/tournaments/12345678/view");
        });
      });
    });

    describe("in edit mode", function() {
      it("sets a header", function() {
        var tournament = new tichu.Tournament(new tichu.TournamentHeader("120489"))
        tournament.name = "Awesome Tournament";
        loadController({
          id: "120489",
          failure: null,
          tournament: tournament
        });
        expect(header.header).toBe("Editing Awesome Tournament");
        expect(header.backPath).toBe("/tournaments/120489/view");
        expect(header.showHeader).toBe(true);
      });

      it("creates a populated TournamentRequest", function() {
        var tournament = new tichu.Tournament(new tichu.TournamentHeader("06089"));
        tournament.name = "Chocolate Tichu";
        tournament.setNoPairs(6, function(pairNo) { return new tichu.TournamentPair(pairNo) });
        tournament.noBoards = 15;
        tournament.pairs[4].setPlayers([
          {name: "player name", email: "player@somewhere.example"}
        ]);

        var tournamentFormController = loadController({
          id: "06089",
          failure: null,
          tournament: tournament
        });
        var player = new tichu.PlayerRequest();
        player.pairNo = 5;
        player.name = "player name";
        player.email = "player@somewhere.example";
        expect(tournamentFormController.tournament.name).toBe("Chocolate Tichu");
        expect(tournamentFormController.tournament.noPairs).toBe(6);
        expect(tournamentFormController.tournament.noBoards).toBe(15);
        expect(tournamentFormController.tournament.players).toEqual([player]);
      });

      it("stores the tournament in the original field", function() {
        var tournament = new tichu.Tournament(new tichu.TournamentHeader("06089"));
        var tournamentFormController = loadController({
          id: "06089",
          failure: null,
          tournament: tournament
        });
        expect(tournamentFormController.original).toBe(tournament);
      });

      it("displays a dialog and sets the failure in case of error", function() {
        var tournamentFormController = loadController({
          id: "123049",
          tournament: null,
          failure: {
            redirectToLogin: false,
            error: "An error happened",
            detail: "It was a very erroneous error"
          }
        });
        expect(tournamentFormController.failure).toBeTruthy();
        expect($mdDialog.show).toHaveBeenCalled();
      });

      it("reloads the page when the dialog is OK'd", function() {
        loadController({
          id: "30926",
          tournament: null,
          failure: {
            redirectToLogin: false,
            error: "An error happened",
            detail: "It was a very erroneous error"
          }
        });
        dialogDeferred.resolve();
        $rootScope.$apply();
        expect($route.reload).toHaveBeenCalled();
      });

      it("leaves for the tournament page when the dialog is canceled", function() {
        $location.url("/tournaments/10927/edit");
        loadController({
          id: "10927",
          tournament: null,
          failure: {
            redirectToLogin: false,
            error: "An error happened",
            detail: "It was a very erroneous error"
          }
        });
        dialogDeferred.reject();
        $rootScope.$apply();
        expect($location.url()).toBe("/tournaments/10927/view");
      });

      it("opens the login page when the dialog is OK'd on a login error", function() {
        $window.location.href = "/tournaments/28372/edit";
        $location.url("/tournaments/28372/edit");
        loadController({
          id: "28372",
          tournament: null,
          failure: {
            redirectToLogin: true,
            error: "Log in already",
            detail: "What are you even doing here"
          }
        });
        dialogDeferred.resolve();
        $rootScope.$apply();
        expect($window.location.href).toBe("/api/login?then=%2Ftournaments%2F28372%2Fedit");
      });

      it("cancels the dialog and doesn't change URLs when the scope is destroyed", function() {
        $location.url("/tournaments/03982/edit");
        loadController({
          id: "03982",
          tournament: null,
          failure: {
            redirectToLogin: false,
            error: "An error happened",
            detail: "It was a very erroneous error"
          }
        });
        scope.$destroy();
        expect($mdDialog.cancel).toHaveBeenCalled();
        $rootScope.$apply();
        expect($location.url()).toBe("/tournaments/03982/edit");
      });

      describe("save", function() {
        beforeEach(function() {
          fakeBackends.install();
        });

        afterEach(function() {
          $httpBackend.verifyNoOutstandingExpectation();
          $httpBackend.verifyNoOutstandingRequest();
        });

        it("starts off not saving", function() {
          var tournamentFormController = loadController({
            id: "72830",
            failure: null,
            tournament: new tichu.Tournament(new tichu.TournamentHeader("72830"))
          });
          expect(tournamentFormController.saving).toBe(false);
        });

        it("sets the saving member to true", function() {
          var tournamentFormController = loadController({
            id: "36203",
            failure: null,
            tournament: new tichu.Tournament(new tichu.TournamentHeader("36203"))
          });

          tournamentFormController.save();

          expect(tournamentFormController.saving).toBe(true);
          $httpBackend.flush();
        });

        it("only saves once even if called multiple times", function() {
          var tournamentFormController = loadController({
            id: "26392",
            failure: null,
            tournament: new tichu.Tournament(new tichu.TournamentHeader("26392"))
          });

          spyOn(tournamentService, "editTournament").and.callThrough();

          tournamentFormController.save();
          tournamentFormController.save();

          expect(tournamentService.editTournament.calls.count()).toBe(1);
          $httpBackend.flush();
        });

        it("calls editTournament with the tournament ID and member", function() {
          var tournamentFormController = loadController({
            id: "92083",
            failure: null,
            tournament: new tichu.Tournament(new tichu.TournamentHeader("92083"))
          });

          fakeBackends.tournaments.push({
            id: "92083",
            name: "My Okay Tournament",
            no_pairs: 4,
            no_boards: 16,
            players: [
              {
                pair_no: 2,
                name: "George",
                email: "curious@yellow.example"
              }
            ]
          });

          tournamentFormController.tournament = makeTournamentRequest({
            name: "My Cool Tournament",
            noPairs: 5,
            noBoards: 15,
            players: [
              makePlayerRequest({
                pairNo: 3,
                name: "A Player",
                email: "aplayer@tichu.example"
              })
            ]
          });

          tournamentFormController.save();

          $httpBackend.flush();
          $rootScope.$apply();

          expect(fakeBackends.tournaments.length).toBe(1);
          expect(fakeBackends.tournaments[0].name).toBe("My Cool Tournament");
          expect(fakeBackends.tournaments[0].no_pairs).toBe(5);
          expect(fakeBackends.tournaments[0].no_boards).toBe(15);
          expect(fakeBackends.tournaments[0].players.length).toBe(1);
          expect(fakeBackends.tournaments[0].players[0].name).toBe("A Player");
          expect(fakeBackends.tournaments[0].players[0].email).toBe("aplayer@tichu.example");
          expect(fakeBackends.tournaments[0].players[0].pair_no).toBe(3);
        });

        it("displays a dialog and exits saving mode if the save fails", function() {
          var tournamentFormController = loadController({
            id: "92019",
            failure: null,
            tournament: new tichu.Tournament(new tichu.TournamentHeader("92019"))
          });

          tournamentFormController.tournament = makeTournamentRequest();
          fakeBackends.requestCrash = true;

          tournamentFormController.save();

          $httpBackend.flush();
          $rootScope.$apply();

          expect($mdDialog.show).toHaveBeenCalled();
          expect(tournamentFormController.saving).toBe(false);
        });

        it("redirects to the new tournament's view page on success", function() {
          fakeBackends.tournaments.push({
            id: "32732",
            name: "My Okay Tournament",
            no_pairs: 4,
            no_boards: 16,
            players: [
              {
                pair_no: 2,
                name: "George",
                email: "curious@yellow.example"
              }
            ],
          });

          $location.url("/tournaments/32732/edit");
          var tournamentFormController = loadController({
            id: "32732",
            tournament: new tichu.Tournament(new tichu.TournamentHeader("32732")),
            failure: null
          });

          tournamentFormController.tournament = makeTournamentRequest();

          tournamentFormController.save();

          $httpBackend.flush();
          $rootScope.$apply();

          expect($mdDialog.show).not.toHaveBeenCalled();
          expect($location.url()).toBe("/tournaments/32732/view");
        });
      });
    });
  });
});