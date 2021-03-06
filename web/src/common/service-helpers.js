/**
 * Namespace containing helper functions for services.
 * @namespace
 */
ServiceHelpers = window.ServiceHelpers || {};

/**
 * Asserts that the given object has the given type.
 *
 * @template T
 * @param {string} context the string describing the value to put in the error message
 * @param {T} value the value to test the type of
 * @param {string} type the type to test for. Can be multiple types, separated by |
 * @param {boolean=} allowNullOrUndefined whether null and undefined are allowed (default false)
 * @returns {T} the original value
 */
ServiceHelpers.assertType = function assertType(context, value, type, allowNullOrUndefined) {
  var actualType;
  if (value === null || value === undefined) {
    if (allowNullOrUndefined) {
      return value;
    } else {
      actualType = '' + value;
    }
  } else {
    actualType = typeof value;
  }

  if (actualType === 'object' && angular.isArray(value)) {
    actualType = 'array';
  } else if (actualType === 'number' && isNaN(value)) {
    actualType = 'NaN';
  }

  var acceptableTypes = type.split('|')
  if (acceptableTypes.indexOf(actualType) < 0) {
    throw new Error(context + " was " + actualType + ", not " + type);
  }
  return value;
};

/**
 * Creates an error handler for the standard API error structure.
 * @param {angular.$q} $q The promise service to reject with.
 * @param {angular.$log} $log The log service to record errors with.
 * @param {string} path The API path that was called and failed.
 * @param {boolean=} accept403 Whether 403 should be treated as needing redirect to login.
 * @returns {function(response:*):angular.$q.Promise<tichu.RpcError>} A response handler.
 */
ServiceHelpers.handleErrorIn = function handleErrorIn($q, $log, path, accept403) {
  accept403 = accept403 || false;
  return function onError(response) {
    var rejection = new tichu.RpcError();
    if (typeof response.status === 'number') {
      $log.error(
          "Got error calling " + path + " (" + response.status + " " + response.statusText + "):\n"
          + JSON.stringify(response.data));
      rejection.redirectToLogin = (response.status === 401) || (accept403 && response.status === 403);
      if (typeof response.data === 'object' && response.data.error && response.data.detail) {
        rejection.error = response.data.error;
        rejection.detail = response.data.detail;
      } else {
        rejection.error = response.statusText + " (" + response.status + ")";
        rejection.detail = response.data;
      }
    } else {
      $log.error(response);
      rejection.redirectToLogin = false;
      rejection.error = "Client Error";
      rejection.detail = "Something unexpectedly went wrong when talking to the server...";
    }
    return $q.reject(rejection);
  }
}