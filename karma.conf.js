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
      'templates/images/*.pt',
      'templates/instances/*.pt',
      'templates/ipaddresses/*.pt',
      'templates/snapshots/*.pt',
      'templates/volumes/*.pt',
      'static/js/thirdparty/modernizr/custom.modernizr.js',
      'static/js/thirdparty/jquery/jquery.min.js',
      'static/js/thirdparty/angular/angular.min.js',
      'static/js/thirdparty/angular/angular-sanitize.min.js',
      'static/js/thirdparty/angular/angular-mocks.js',
      'static/js/thirdparty/jquery/jquery.generateFile.js',
      'static/js/widgets/notify.js',
      'static/js/pages/eucaconsole_utils.js',
      'static/js/thirdparty/jquery/chosen.jquery.min.js',
      'static/js/thirdparty/utils/purl.js',
      'static/js/thirdparty/codemirror/codemirror.js',
      'static/js/thirdparty/jasmine/jasmine-jquery.js',
      'static/js/pages/custom_filters.js',
      'static/js/widgets/autoscale_tag_editor.js',
      'static/js/widgets/bdmapping_editor.js',
      'static/js/widgets/image_picker.js',
      'static/js/widgets/policy_list.js',
      'static/js/widgets/quotas.js',
      'static/js/widgets/s3_metadata_editor.js',
      'static/js/widgets/s3_sharing_panel.js',
      'static/js/widgets/securitygroup_rules.js',
      'static/js/widgets/tag_editor.js',
      'static/js/widgets/user_editor.js',
      'static/js/pages/keypair.js',
      'static/js/pages/image.js',
      'static/js/pages/instance.js',
      'static/js/pages/instance_launch.js',
      'static/js/pages/ipaddress.js',
      'static/js/pages/launchconfig_wizard.js',
      'static/js/pages/scalinggroup_wizard.js',
      'static/js/pages/snapshot.js',
      'static/js/pages/volume.js',
      'static/js/jasmine-spec/SpecHelper.js',
      'static/js/jasmine-spec/spec_autoscale_tag_editor.js',
      'static/js/jasmine-spec/spec_bdmapping_editor.js',
      'static/js/jasmine-spec/spec_image_picker.js',
      'static/js/jasmine-spec/spec_policy_list.js',
      'static/js/jasmine-spec/spec_quotas.js',
      'static/js/jasmine-spec/spec_s3_metadata_editor.js',
      'static/js/jasmine-spec/spec_s3_sharing_panel.js',
      'static/js/jasmine-spec/spec_security_group_rules.js',
      'static/js/jasmine-spec/spec_tag_editor.js',
      'static/js/jasmine-spec/spec_user_editor.js',
      'static/js/jasmine-spec/spec_image.js',
      'static/js/jasmine-spec/spec_instance.js',
      'static/js/jasmine-spec/spec_instance_launch.js',
      'static/js/jasmine-spec/spec_ipaddress.js',
      'static/js/jasmine-spec/spec_keypair.js',
      'static/js/jasmine-spec/spec_launchconfig_wizard.js',
      'static/js/jasmine-spec/spec_scalinggroup_wizard.js',
      'static/js/jasmine-spec/spec_snapshot.js',
      'static/js/jasmine-spec/spec_volume.js'
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
