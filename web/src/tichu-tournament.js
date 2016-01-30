(function(angular) {
  /**
   * Dumb test function to get some hello world up in here.
   *
   * @ngInject
   * @param {angular.Scope} $rootScope The root scope to fill in a stupid parameter on.
   */
  function initializeRootScope($rootScope) {
    $rootScope.tichu = "Grand Tichu";
  }

  angular.module("tichu-tournament", ["ng"])
      .run(initializeRootScope);
})(angular);