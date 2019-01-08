"use strict";
(function(angular) {
  /**
   * Main controller for the tournament edit page.
   *
   * @constructor
   * @param {!angular.Scope} $scope
   * @param {$mdSidenav} $mdSidenav
   * @param {$mdMedia} $mdMedia
   * @param {$mdToast} $mdToast
   * @param {TichuTournamentService} TichuTournamentService
   * @param {$mdDialog} $mdDialog
   * @param {angular.$window} $window
   * @param {angular.$location} $location
   * @param {$route} $route
   * @param {!{failure: ?tichu.RpcError, id: ?string, tournamentStatus: ?tichu.TournamentStatus}} loadResults
   * @ngInject
   */
  function EmailCenterController($scope, $mdSidenav, $mdMedia, $mdToast, TichuTournamentService, $mdDialog, $log, $window, $location, $route, loadResults) {
    var backPath = "/tournaments" + (loadResults.id ? "/" + loadResults.id + "/view" : "");
    $scope.appController.setPageHeader({
      header: loadResults.failure
          ? "Tournament Error"
          : "Email Center",
      backPath: $mdMedia('gt-sm') ? backPath : null,
      showHeader: true,
      showMenu: !$mdMedia('gt-sm'),
      openMenu: function() {
        $mdSidenav('left').toggle();
      },
    });

    $scope.$on('$locationChangeStart', 
      function(event) {
        if (angular.element(document.body).hasClass('md-dialog-is-showing')) {
          event.preventDefault();
          $mdDialog.cancel();
       }
     });

    /**
     * The logging service injected at creation.
     * @type {$log}
     * @private
     */
    this._$log = $log;

    /** The location service injected at creation. */
    this._$location = $location;

    /** The scope this controller exists in. */
    this._$scope = $scope;

    /**
     * The toast service injected at creation.
     * @type {$mdToast}
     * @private
     */
    this._$mdToast = $mdToast;

    /**
     * The dialog service injected at creation.
     * @type {$mdDialog}
     * @private
     */
    this._$mdDialog = $mdDialog;

    /**
     * The tournament service injected at creation.
     * @type {TichuTournamentService}
     * @private
     */
    this._tournamentService = TichuTournamentService;

    /**
     * The details about the failure, if there was one.
     *
     * @type {tichu.RpcError}
     */
    this.failure = loadResults.failure;
    
    /**
     * The full tournament details loaded on startup.
     *
     * @type {tichu.Tournament}
     */
    this.tournament = loadResults.tournament
    
    /**
     * Tournament id.
     * @type {string}
     */
    this.id = this.tournament._header.id;

    /**
     * Tournament name.
     * @type {string}
     */
    this.name = this.tournament._header.name;

    /**
     * Model for the selected email type.
     * @type {string}
     */
    this.emailType = null;
    /**
     * Model for those players who have emails.
     * @type {tichu.TournamentPlayer[]}
     */
    this.playersWithEmail = this.tournament.pairs.map(getPlayers).flat().filter(hasEmail);
    /**
     * Model for those players whose checkboxes are selected.
     * @type {tichu.TournamentPlayer[]}
     */
    this.selectedPlayers = this.tournament.pairs.map(getPlayers).flat().filter(hasEmail);
    /**
     * Array that keeps track of which teams are missing players with emails. 
     * @type {number[]} For each team i, the i-1st index of the array contains
     *                the number of members in the pair that are missing an email.
     */
    this.missingEmailsPerPair = countMissingEmails(this.tournament.pairs);
    /**
     * Total number of players that are missing email addresses. 
     * @type {number}
     */
    this.numMissingEmails = this.missingEmailsPerPair.reduce(function(a, b) {return a + b;});

    /**
     * Whether the UI is currently sending a request for an email.
     * @type {boolean}
     */
    this.sending = false;

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

  /* 
   * Helper function, returns true if a player has an email.
   * @param {tichu.TournamentPlayer} player
   */
  function hasEmail(player) {
    return player.email != undefined && player.email != "";
  }

  /* 
   * Helper getter, returns the players of a pair.
   * @param {tichu.TournamentPair} pair
   */
  function getPlayers(pair) {
    return pair.players;
  }

  /* 
   * Helper function, returns the number of players in a pair (between 0 and 2)
   * who do not have an email address.
   * @param {tichu.TournamentPair} pair
   */
  function countMissingEmailsInPair(pair) {
    return 2 - pair.players.filter(function (p) {return hasEmail(p); }).length;
  }
  
  /**
   * Returns an array of integers where the ith index represents the number
   * of members of team i+1 who are missing emails.
   * @param {tichu.TournamentPair[]} pairs
   */
  function countMissingEmails(pairs) {
    return pairs.map(countMissingEmailsInPair);
  }

  /**
   * Sends a request to the server to send an email to the selected recipients.
   */
  EmailCenterController.prototype.sendEmail = function sendEmail() {
    if (this.sending) {
      return;
    }
    this.sending = true;
    var self = this;
    var selectedPlayers = this.selectedPlayers;
    var tournamentId = this.id;
    var tournamentService = this._tournamentService;
    var $mdToast = this._$mdToast;
    var $mdDialog = this._$mdDialog;
    var confirmation_text = "Send " + this.emailType + " email to " +
                            selectedPlayers.length + " recipient" + 
                            (selectedPlayers.length == 1 ? "" : "s") + "?";
    var dialog = this._$mdDialog.confirm()
        .title("Send Email?")
        .textContent(confirmation_text)
        .ok("Send")
        .cancel("Cancel");
    this._$mdDialog.show(dialog).then(function () {
      var request = new tichu.EmailRequest();
      request.emails = selectedPlayers.map(function (p) {return p.email;})
      var promise = self.emailType == "WELCOME" ? tournamentService.sendWelcomeEmail(request, tournamentId)
                                                : tournamentService.sendResultsEmail(request, tournamentId);
      promise.then(function(result) {
        self.sending = false;
        $mdToast.showSimple("Email sent");
      }).catch(function(failure) {
        var alert = $mdDialog.alert()
          .title(failure.error)
          .textContent(failure.detail)
          .ok("Try again");
        $mdDialog.show(alert)
        self.sending = false;
      });
    }, function (autoHidden) {
        self.sending = false;
    });
  }

  /* Executed when the SelectAll checkbox is clicked. */
  EmailCenterController.prototype.selectAll = function selectAll() {
    if (this.selectedPlayers.length != this.playersWithEmail.length) {
      this.selectedPlayers = this.playersWithEmail.slice(0);
    } else {
      this.selectedPlayers = [];
    }
  }

  /* Executed when the checkbox for a specific player is clicked. */
  EmailCenterController.prototype.toggle = function toggle(player) {
    var idx = this.selectedPlayerIndex(player);
    if (idx > -1) {
      this.selectedPlayers.splice(idx, 1);
    } else {
      this.selectedPlayers.push(player);
    }
  }

  /* 
   * Finds the index of a specific player in the selectedPlayers array
   * Returns -1 if the player is absent entirely.
   */
  EmailCenterController.prototype.selectedPlayerIndex = function selectedPlayerIndex(player) {
    for (var i = 0; i < this.selectedPlayers.length; i++) {
      var current_player = this.selectedPlayers[i];
      if (current_player.name == player.name && current_player.email == player.email) {
        return i;
      }
    }
    return -1;
  }

  /* Finds whether a specific player is selected. */
  EmailCenterController.prototype.isSelected = function isSelected(player) {
    return this.selectedPlayerIndex(player) > -1;
  }

  /* Determines whether all players are selected */
  EmailCenterController.prototype.isSelectAllChecked = function isSelectAllChecked() {
    return this.selectedPlayers.length === this.playersWithEmail.length;
  }

  /* 
   * Determines whether the select all checkbox is in an indeterminate state. 
   * This happens when not all and not 0 players are selected.
   */
  EmailCenterController.prototype.isSelectAllIndeterminate = function isSelectAllIndeterminate() {
    return this.selectedPlayers.length != this.playersWithEmail.length && 
           this.selectedPlayers.length != 0;
  }

  /* Determines whether the send email button should be disabled */
  EmailCenterController.prototype.isButtonDisabled = function isButtonDisabled() {
    return this.sending || this.selectedPlayers.length == 0 || this.emailType == null;
  }

  /**
   * Asynchronously loads the requested tournament.
   *
   * @param {TichuTournamentService} tournamentService
   * @param {string} id
   * @return {!angular.$q.Promise<!{failure: ?tichu.RpcError, tournament: ?tichu.Tournament}>}
   */
  function loadTournament(tournamentService, id) {
    return tournamentService.getTournament(id).then(function(result) {
      return {
        tournament: result
      };
    }).catch(function(rejection) {
      return {
        failure: rejection
      };
    });
  }

  /**
   * Configures the routing provider to load the email center at its path.
   *
   * @param {!$routeProvider} $routeProvider
   * @ngInject
   */
  function mapRoute($routeProvider) {
    $routeProvider
        .when("/tournaments/:id/email", {
          templateUrl: "src/tournaments/email-center.html",
          controller: "EmailCenterController",
          controllerAs: "emailCenterController",
          resolve: {
            "loadResults": /** @ngInject */ function($route, TichuTournamentService) {
              return loadTournament(TichuTournamentService, $route.current.params["id"]);
            }
          }
        });
  }

  angular.module("email-center", ["ng", "ngRoute", "ngMaterial", "tichu-tournament-service"])
      .controller("EmailCenterController", EmailCenterController)
      .config(mapRoute);
})(angular);