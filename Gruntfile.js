
module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
      pkg: grunt.file.readJSON('package.json'),
      bowercopy: {
          options: {
              // Bower components folder will be removed afterwards
              clean: true
          },
          angular: {
              options: {
                  destPrefix: 'eucaconsole/static/js/thirdparty/angular'
              },
              files: {
                'angular.min.js': 'angular/angular.min.js',
                'angular-sanitize.min.js': 'angular-sanitize/angular-sanitize.min.js',
                'angular-mocks.js': 'angular-mocks/angular-mocks.js'
              }
          },
          jquery: {
              options: {
                  destPrefix: 'eucaconsole/static/js/thirdparty/jquery'
              },
              files: {
                'jquery.min.js': 'jquery/jquery.min.js'
              }
          },
          jasmine: {
              options: {
                  destPrefix: 'eucaconsole/static/js/thirdparty/jasmine'
              },
              files: {
                'jasmine_favicon.png': 'jasmine/images/jasmine_favicon.png',
                'jasmine.css': 'jasmine/lib/jasmine-core/jasmine.css',
                'jasmine.js': 'jasmine/lib/jasmine-core/jasmine.js',
                'jasmine-html.js': 'jasmine/lib/jasmine-core/jasmine-html.js',
                'console.js': 'jasmine/lib/console/console.js',
                'boot.js': 'jasmine/lib/jasmine-core/boot/boot.js'
              }
          },
          jasmine_jquery: {
              options: {
                  destPrefix: 'eucaconsole/static/js/thirdparty/jasmine'
              },
              files: {
                'jasmine-jquery.js': 'jasmine-jquery/lib/jasmine-jquery.js'
              }
          },
      },
      jshint: {
          options: {
              reporter: require('jshint-stylish')
          },
          all: ['Gruntfile.js',
                'eucaconsole/static/js/pages/*.js',
                'eucaconsole/static/js/widgets/*.js',
                'eucaconsole/static/js/jasmine-spec/*.js']
      },
      karma: {
          unit: {
              configFile: 'karma.conf.js'
          },
          ci: {
              configFile: 'karma.conf.js',
              singleRun: true,
          }
      },
      clean: {
          min: ["eucaconsole/static/js/minified"]
      },
      uglify: {
          my_target: {
              options: {
                  mangle: false,
                  compress: {
                      drop_console: true
                  }
              },
              files: [
                  {
                      expand: true,     // Enable dynamic expansion.
                      cwd: 'eucaconsole/static/js/',      // Src matches are relative to this path.
                      src: ['pages/*.js', 'widgets/*.js'], // Actual pattern(s) to match.
                      dest: 'eucaconsole/static/js/minified/',   // Destination path prefix.
                      ext: '.min.js',   // Dest filepaths will have this extension.
                      extDot: 'first'   // Extensions in filenames begin after the first dot
                  },
              ]
          }
      },
      watch: {
          scripts: {
              files: ['eucaconsole/static/js/**/*.js'],
              tasks: ['karma:ci', 'jshint'],
              options: {
                  spawn: false,
              },
          },
      }
  });

  // Load the plugins
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-bowercopy');
  grunt.loadNpmTasks('grunt-karma');

  // Default task(s).
  grunt.registerTask('default', ['watch']);

};
