/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
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
