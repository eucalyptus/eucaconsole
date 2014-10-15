beforeEach(function () {
  jasmine.addMatchers({
    toBeEmptyArray: function () {
      return {
        compare: function (actual) {
          return {
            pass: actual.length === 0 
          }
        }
      };
    }
  });
});
