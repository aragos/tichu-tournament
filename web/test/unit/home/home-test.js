"use strict";
describe("tichu-home module", function() {
  beforeEach(module("tichu-home"));

  describe("HomeController controller", function() {
    var scope;
    var $rootScope;
    var header;
    var $controller;
    var $route;
    var $mdDialog;
    var $location;
    var $window;
    var dialogDeferred;
    var codeService;

    beforeEach(module(function($provide) {
      $window = {location: {href: "/home"}};
      $provide.value("$window", $window);
      $provide.service("TichuCodeService", function($q) {
        return {
          codes: [],
          deferred: null,
          getMovementForCode: function(code) {
            this.codes.push(code);
            this.deferred = $q.defer();
            return this.deferred.promise;
          }
        };
      });
    }));

    beforeEach(inject(function(/** angular.Scope */ _$rootScope_,
                               /** angular.$q */ $q,
                               /** angular.$controller */ _$controller_,
                               /** $route */ _$route_,
                               /** angular.$location */ _$location_,
                               /** $mdDialog */ _$mdDialog_,
                               /** TichuCodeService */ TichuCodeService) {
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
      codeService = TichuCodeService;
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
      });
    }));

    /**
     * Starts up the controller.
     *
     * @returns {HomeController}
     */
    function loadController() {
      return $controller("HomeController as homeController", {
        "$scope": scope
      });
    }

    it("disables the header", function() {
      loadController();
      expect(header.showHeader).toBe(false);
    });

    it("starts off not loading", function() {
      var homeController = loadController();
      expect(homeController.loading).toBe(false);
    });

    it("switches to loading when a code is loaded", function() {
      var homeController = loadController();

      homeController.code = "DOGS";
      homeController.loadCode();

      expect(homeController.loading).toBe(true);
    });

    it("calls the code service with the code from the scope", function() {
      var homeController = loadController();

      homeController.code = "CATS";
      homeController.loadCode();

      expect(codeService.codes).toEqual(["CATS"]);
    });

    it("uppercases the code in the scope if it wasn't already", function() {
      var homeController = loadController();

      homeController.code = "kits";
      homeController.loadCode();

      expect(homeController.code).toBe("KITS");
      expect(codeService.codes).toEqual(["KITS"]);
    });

    it("does not call the code service again if it is already loading", function() {
      var homeController = loadController();

      homeController.code = "CATS";
      homeController.loadCode();
      homeController.loadCode();

      expect(codeService.codes).toEqual(["CATS"]);
    });

    it("redirects to the loaded tournament ID and pair number and code on success", function() {
      $location.url("/home");
      var homeController = loadController();

      homeController.code = "RATS";
      homeController.loadCode();

      codeService.deferred.resolve({tournamentId: "987654321", pairNo: 3});
      $rootScope.$apply();
      expect($mdDialog.show).not.toHaveBeenCalled();
      expect(homeController.loading).toBe(true);
      expect($location.url()).toBe("/tournaments/987654321/movement/3?playerCode=RATS");
    });

    it("shows a dialog and stops loading when the call fails", function() {
      $location.url("/home");
      var homeController = loadController();

      homeController.code = "BALZ";
      homeController.loadCode();

      codeService.deferred.reject({redirectToLogin: false, error: "WHAT IS THAT CODE", detail: "LEWD"});
      $rootScope.$apply();
      expect(homeController.loading).toBe(false);
      expect($location.url()).toBe("/home");
    });

    it("shows a dialog and turns off the loading indicator when the call fails", function() {
      $location.url("/home");
      var homeController = loadController();

      homeController.code = "HIPZ";
      homeController.loadCode();

      codeService.deferred.reject({redirectToLogin: false, error: "WHAT IS THAT CODE", detail: "OMG LEWD"});
      $rootScope.$apply();
      expect(homeController.loading).toBe(false);
      expect($location.url()).toBe("/home");
      expect($mdDialog.show).toHaveBeenCalled();
    });
  });
});