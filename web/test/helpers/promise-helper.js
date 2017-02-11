"use strict";
/**
 * @typedef {function(promise:angular.$q.Promise, options:{expectSuccess:boolean=, expectFailure:boolean=, expectUnfinished:boolean=, flushHttp:(number|boolean)=}):*}
 */
var PromiseHelper;
/**
 * Returns a helper function used to invoke promises and check the results.
 * @param {$rootScope.Scope} $rootScope
 * @param {$httpBackend=} $httpBackend
 * @returns {PromiseHelper}
 */
function promiseHelper($rootScope, $httpBackend) {
  return function runPromise(promise, options) {
    var result = {};
    promise.then(function(promiseResolvedWith) {
      result = {
        promise_resolved_with: promiseResolvedWith === undefined ? "(undefined)" : promiseResolvedWith,
        actual_result: promiseResolvedWith
      };
    }).catch(function(promiseFailedWith) {
      result = {
        promise_failed_with: promiseFailedWith === undefined ? "(undefined)" : promiseFailedWith,
        actual_result: promiseFailedWith
      };
    });
    if (options.flushHttp && $httpBackend) {
      if (typeof options.flushHttp === 'number') {
        $httpBackend.flush(options.flushHttp);
      } else {
        $httpBackend.flush();
      }
    }
    $rootScope.$apply();
    if (options.expectSuccess) {
      expect(result.promise_failed_with).toBeUndefined();
      expect(result.promise_resolved_with).toBeDefined();
    } else if (options.expectFailure) {
      expect(result.promise_resolved_with).toBeUndefined();
      expect(result.promise_failed_with).toBeDefined();
    } else if (options.expectUnfinished) {
      expect(result.promise_resolved_with).toBeUndefined();
      expect(result.promise_failed_with).toBeUndefined();
    }
    return result.actual_result;
  }
}