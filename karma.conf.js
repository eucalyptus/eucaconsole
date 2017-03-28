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
      'templates/**/*.pt',
      'static/html/directives/*.html',
      'static/js/thirdparty/modernizr/custom.modernizr.js',
      'static/js/thirdparty/jquery/jquery.min.js',
      'static/js/thirdparty/angular/angular.min.js',
      'static/js/thirdparty/angular/angular-sanitize.min.js',
      'static/js/thirdparty/angular/angular-mocks.js',
      'static/js/thirdparty/angular/angular-smart-table.js',
      'static/js/thirdparty/angular/angular-route.min.js',
      'static/js/thirdparty/angular/chosen.js',
      'static/js/thirdparty/jquery/jquery.generateFile.js',
      'static/js/thirdparty/jquery/jquery.base64.js',
      'static/js/thirdparty/jquery/jquery.cookie.js',
      'static/js/thirdparty/foundation/foundation.js',
      'static/js/thirdparty/foundation-datepicker/foundation-datepicker.js',
      'static/js/pages/eucaconsole_utils.js',
      'static/js/thirdparty/jquery/jquery-1.11.0-ui.js',
      'static/js/thirdparty/jquery/jquery.cookie.js',
      'static/js/thirdparty/jquery/chosen.jquery.min.js',
      'static/js/thirdparty/utils/purl.js',
      'static/js/thirdparty/utils/hmac-sha256.js',
      'static/js/thirdparty/utils/enc-base64.js',
      'static/js/thirdparty/codemirror/codemirror.js',
      'static/js/thirdparty/codemirror/javascript.js',
      'static/js/thirdparty/codemirror/active-line.js',
      'static/js/thirdparty/jasmine/jasmine-jquery.js',
      'static/js/thirdparty/magic-search/magic_search.js',
      'static/js/widgets/**/*.js',
      'static/js/pages/custom_filters.js',
      'static/js/pages/landingpage.js',
      'static/js/pages/account.js',
      'static/js/pages/account_new.js',
      'static/js/pages/accounts.js',
      'static/js/pages/buckets.js',
      'static/js/pages/bucket_new.js',
      'static/js/pages/bucket_contents.js',
      'static/js/pages/bucket_details.js',
      'static/js/pages/bucket_item_details.js',
      'static/js/pages/bucket_upload.js',
      'static/js/pages/create_alarm.js',
      'static/js/pages/dashboard.js',
      'static/js/pages/group.js',
      'static/js/pages/groups.js',
      'static/js/pages/iam_policy_wizard.js',
      'static/js/pages/image.js',
      'static/js/pages/images.js',
      'static/js/pages/instance.js',
      'static/js/pages/instances.js',
      'static/js/pages/instance_create_ebs_image.js',
      'static/js/pages/instance_create_image.js',
      'static/js/pages/instance_launch.js',
      'static/js/pages/instance_launch_more.js',
      'static/js/pages/instance_types.js',
      'static/js/pages/instance_volumes.js',
      'static/js/pages/ipaddress.js',
      'static/js/pages/ipaddresses.js',
      'static/js/pages/landingpage.js',
      'static/js/pages/login.js',
      'static/js/pages/keypair.js',
      'static/js/pages/keypairs.js',
      'static/js/pages/launchconfig.js',
      'static/js/pages/launchconfigs.js',
      'static/js/pages/launchconfig_wizard.js',
      'static/js/pages/role.js',
      'static/js/pages/roles.js',
      'static/js/pages/scalinggroup.js',
      'static/js/pages/scalinggroups.js',
      'static/js/pages/scalinggroup_instances.js',
      'static/js/pages/scalinggroup_policies.js',
      'static/js/pages/scalinggroup_policy.js',
      'static/js/pages/scalinggroup_wizard.js',
      'static/js/pages/securitygroup.js',
      'static/js/pages/securitygroups.js',
      'static/js/pages/snapshot.js',
      'static/js/pages/snapshots.js',
      'static/js/pages/users.js',
      'static/js/pages/user_new.js',
      'static/js/pages/user_view.js',
      'static/js/pages/volume.js',
      'static/js/pages/volumes.js',
      'static/js/pages/volume_snapshots.js',
      'static/js/pages/elb-wizard/wizard.js',   // Ensuring this file is loaded first, the * below picks up the rest
      'static/js/pages/elb-wizard/*.js',
      'static/js/pages/reporting.js',
      'static/js/pages/usage_reports.js',
      'static/js/services/**/*.js',
      'static/js/jasmine-spec/**/*.js'
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
