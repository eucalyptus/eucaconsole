// Karma configuration
// Generated on Wed Oct 22 2014 18:54:08 GMT-0700 (PDT)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: './eucaconsole/',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine'],


    // list of files / patterns to load in the browser
    files: [
      'templates/panels/*.pt',
      'static/js/thirdparty/modernizr/custom.modernizr.js',
      'static/js/thirdparty/jquery/jquery.min.js',
      'static/js/thirdparty/angular/angular.min.js',
      'static/js/thirdparty/angular/angular-sanitize.min.js',
      'static/js/thirdparty/angular/angular-mocks.js',
      'static/js/thirdparty/jquery/jquery.generateFile.js',
      'static/js/widgets/notify.js',
      'static/js/pages/eucaconsole_utils.js',
      'static/js/thirdparty/jquery/chosen.jquery.min.js',
      'static/js/thirdparty/jasmine/jasmine-jquery.js',
      'static/js/pages/custom_filters.js',
      'static/js/widgets/securitygroup_rules.js',
      'static/js/pages/keypair.js',
      'static/js/jasmine-spec/SpecHelper.js',
      'static/js/jasmine-spec/spec_security_group_rules.js',
      'static/js/jasmine-spec/spec_keypair.js'
    ],


    // list of files to exclude
    exclude: [
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
        '**/*.pt': ['html2js']
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress'],


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['PhantomJS'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false 
  });
};
