"use strict";
describe("ServiceHelpers", function() {
  describe("assertType", function() {
    it("returns the exact original value if it is the correct type", function() {
      var object = {};
      expect(ServiceHelpers.assertType("context", object, "object")).toBe(object);
    });
    it("includes the expected type in the exception message if it is incorrect", function() {
      expect(ServiceHelpers.assertType.bind(null, "context", "5", "number")).toThrowError(/\bnumber\b/);
    });
    it("includes the actual type in the exception message if it is incorrect", function() {
      expect(ServiceHelpers.assertType.bind(null, "context", "[]", "array")).toThrowError(/\bstring\b/);
    });
    it("includes the context in the exception message if the assertion fails", function() {
      expect(ServiceHelpers.assertType.bind(null, "context", NaN, "string")).toThrowError(/\bcontext\b/);
    });

    it("allows null if specifically permitted", function() {
      expect(ServiceHelpers.assertType("context", null, "object", true)).toBeNull();
    });
    it("allows undefined if specifically permitted", function() {
      expect(ServiceHelpers.assertType("context", undefined, "object", true)).toBeUndefined();
    });

    it("does not accept NaN as a number", function() {
      expect(ServiceHelpers.assertType.bind(null, "context", NaN, "number")).toThrowError(/\bNaN\b/);
    });
    it("does not accept NaN as a number even if allowNullOrUndefined is true", function() {
      expect(ServiceHelpers.assertType.bind(null, "context", NaN, "number", true)).toThrowError(/\bNaN\b/);
    });

    describe('string', typeAssertionSuite({
      type: 'string',
      correctExamples: ['abc', ''],
      incorrectExamples: [true, 1, [], {}, null, undefined]
    }));

    describe('number', typeAssertionSuite({
      type: 'number',
      correctExamples: [1, 2.5, -999],
      incorrectExamples: [NaN, true, 'abc', [], {}, null, undefined]
    }));

    describe('boolean', typeAssertionSuite({
      type: 'boolean',
      correctExamples: [true, false],
      incorrectExamples: ['abc', 1, [], {}, null, undefined]
    }));

    describe('array', typeAssertionSuite({
      type: 'array',
      correctExamples: [[1, 2, 3], []],
      incorrectExamples: [true, 1, 'abc', {}, null, undefined]
    }));

    describe('object', typeAssertionSuite({
      type: 'object',
      correctExamples: [{}, {length: 2, 0: 1, 1: 2}],
      incorrectExamples: [true, 1, [], 'abc', null, undefined]
    }));

    describe('null', typeAssertionSuite({
      type: 'null',
      correctExamples: [null],
      incorrectExamples: [true, 1, [], {}, 'abc', undefined]
    }));

    describe('undefined', typeAssertionSuite({
      type: 'undefined',
      correctExamples: [undefined],
      incorrectExamples: [true, 1, [], {}, null, 'abc']
    }));

    /**
     * Generates a test suite for assertType.
     *
     * @param {{type:string, correctExamples:Array, incorrectExamples:Array, allowNullOrUndefined:boolean=}} settings
     * @returns {Function}
     */
    function typeAssertionSuite(settings) {
      return function() {
        settings.correctExamples.forEach(function(example) {
          it("matches " + JSON.stringify(example) + " as " + settings.type
              + (settings.hasOwnProperty('allowNullOrUndefined')
                  ? ' with allowNullOrUndefined ' + settings.allowNullOrUndefined : ""), function() {
            expect(ServiceHelpers.assertType("", example, settings.type, settings.allowNullOrUndefined)).toBe(example);
          });
        });
        settings.incorrectExamples.forEach(function(example) {
          it("does not match " + JSON.stringify(example) + " as " + settings.type
              + (settings.hasOwnProperty('allowNullOrUndefined')
                  ? ' with allowNullOrUndefined ' + settings.allowNullOrUndefined : ""), function() {
            expect(ServiceHelpers.assertType.bind(
                null, "", example, settings.type, settings.allowNullOrUndefined)).toThrow();
          });
        });
      }
    }
  });
});