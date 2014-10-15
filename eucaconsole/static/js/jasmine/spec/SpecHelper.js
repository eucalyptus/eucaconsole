beforeEach(function () {
  jasmine.addMatchers({
    toBePlaying: function () {
      return {
        compare: function (actual, expected) {
          var player = actual;

          return {
            pass: player.currentlyPlayingSong === expected && player.isPlaying
          }
        }
      };
    },
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
