"use strict";
describe("tichu-tournament module", function() {
  beforeEach(module("tichu-tournament"));

  describe("default routing", function() {
    var $rootScope;
    var $location;
    var $route;

    beforeEach(inject(function(/** $location */ _$location_,
                               /** $route */ _$route_,
                               /** $rootScope */ _$rootScope_) {
      $rootScope = _$rootScope_;
      $route = _$route_;
      $location = _$location_;
    }));

    it("routes to /home by default", function() {
      $location.path("/");
      $rootScope.$digest();
      expect($location.path()).toBe("/home");
    });

    it("redirects old-style tournament URLs to new-style ones", function() {
      $location.path("/tournaments/91820");
      $rootScope.$digest();
      expect($location.path()).toBe("/tournaments/91820/view");
    });

    it("redirects old-style tournament URLs with trailing slash to new-style ones", function() {
      $location.path("/tournaments/91820/");
      $rootScope.$digest();
      expect($location.path()).toBe("/tournaments/91820/view");
    });

    it("leaves tournament URLs with extra stuff after alone", function() {
      $location.path("/tournaments/91820/junk");
      $rootScope.$digest();
      expect($location.path()).toBe("/home");
    });
  });

  describe("AppController controller", function() {
    var $rootScope;
    var scope;
    var /** AppController */ appController;
    var /** angular.$q */ $q;

    beforeEach(inject(function (/** angular.Scope */ _$rootScope_,
                                /** angular.$controller */ $controller,
                                /** angular.$q */ _$q_) {
      $rootScope = _$rootScope_;
      scope = $rootScope.$new(false);
      appController = $controller("AppController as appController", {"$scope": scope});
      $q = _$q_;
    }));

    it("sets a header and title", function () {
      expect(appController.header).toBe("Tichu Tournament");
      expect(appController.title).toBe("Tichu Tournament");
    });

    describe("setPageHeader", function() {
      it("defaults to clearing everything, but leaving the header visible", function() {
        appController.setPageHeader({});

        expect(appController.title).toBe("Tichu Tournament");
        expect(appController.header).toBe(null);
        expect(appController.backPath).toBe(null);
        expect(appController.showHeader).toBe(true);
        expect(appController.refresher).toBe(null);
        expect(appController.refreshStatus).toBe(true);
      });

      it("sets the header from the options", function() {
        appController.setPageHeader({header: "Page"});

        expect(appController.header).toBe("Page");
      });

      it("sets the back path from the options", function() {
        appController.setPageHeader({backPath: "/home"});

        expect(appController.backPath).toBe("/home");
      });

      it("turns off the header display if showHeader is false", function() {
        appController.setPageHeader({showHeader: false});

        expect(appController.showHeader).toBe(false);
      });

      it("updates the refresher function when set", function() {
        function refresher() {}

        appController.setPageHeader({refresh: refresher});

        expect(appController.refresher).toBe(refresher);
      });
    });

    describe("refresh", function() {
      it("does nothing if the refresher function is not set", function() {
        appController.setPageHeader({refresher: null});

        appController.refresh();

        expect(appController.refreshStatus).toBe(true);
      });

      it("sets the refresh status null when first called", function() {
        appController.setPageHeader({refresh: function() {
          return $q.defer().promise;
        }});

        appController.refresh();

        expect(appController.refreshStatus).toBe(null);
      });

      it("sets the refresh status true when the promise resolves", function() {
        var deferred = $q.defer();
        appController.setPageHeader({refresh: function() {
          return deferred.promise;
        }});

        appController.refresh();
        deferred.resolve();
        $rootScope.$apply();

        expect(appController.refreshStatus).toBe(true);
      });

      it("sets the refresh status false when the promise rejects", function() {
        var deferred = $q.defer();
        appController.setPageHeader({refresh: function() {
          return deferred.promise;
        }});

        appController.refresh();
        deferred.reject();
        $rootScope.$apply();

        expect(appController.refreshStatus).toBe(false);
      });
    })
  });
});