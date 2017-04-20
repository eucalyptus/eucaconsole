/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview helper function
 * @requires Jasmine
 *
 */
beforeEach(function () {
  jasmine.addMatchers({
    toBeEmptyArray: function () {
      return {
        compare: function (actual) {
          return {
            pass: actual.length === 0
          };
        }
      };
    }
  });
});
