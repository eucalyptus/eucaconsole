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
      'templates/*.pt',
      'templates/panels/*.pt',
      'templates/accounts/*.pt',
      'templates/buckets/*.pt',
      'templates/dialogs/*.pt',
      'templates/elbs/**/*.pt',
      'templates/dashboard.pt',
      'templates/groups/*.pt',
      'templates/images/*.pt',
      'templates/instances/*.pt',
      'templates/ipaddresses/*.pt',
      'templates/keypairs/*.pt',
      'templates/launchconfigs/*.pt',
      'templates/policies/*.pt',
      'templates/roles/*.pt',
      'templates/scalinggroups/*.pt',
      'templates/securitygroups/*.pt',
      'templates/snapshots/*.pt',
      'templates/users/*.pt',
      'templates/volumes/*.pt',
      'static/html/directives/*.html',
      'static/js/thirdparty/modernizr/custom.modernizr.js',
      'static/js/thirdparty/jquery/jquery.min.js',
      'static/js/thirdparty/angular/angular.min.js',
      'static/js/thirdparty/angular/angular-sanitize.min.js',
      'static/js/thirdparty/angular/angular-mocks.js',
      'static/js/thirdparty/angular/angular-smart-table.js',
      'static/js/thirdparty/angular/angular-route.min.js',
      'static/js/thirdparty/jquery/jquery.generateFile.js',
      'static/js/thirdparty/jquery/jquery.base64.js',
      'static/js/thirdparty/jquery/jquery.cookie.js',
      'static/js/thirdparty/foundation/foundation.js',
      'static/js/thirdparty/foundation-datepicker/foundation-datepicker.js',
      'static/js/widgets/notify.js',
      'static/js/widgets/modal.js',
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
      'static/js/pages/custom_filters.js',
      'static/js/widgets/form_components.js',
      'static/js/widgets/autoscale_tag_editor.js',
      'static/js/widgets/bdmapping_editor.js',
      'static/js/widgets/image_picker.js',
      'static/js/widgets/create_bucket_dialog.js',
      'static/js/widgets/policy_list.js',
      'static/js/widgets/quotas.js',
      'static/js/widgets/s3_metadata_editor.js',
      'static/js/widgets/s3_sharing_panel.js',
      'static/js/widgets/securitygroup_rules.js',
      'static/js/widgets/tag_editor.js',
      'static/js/widgets/user_editor.js',
      'static/js/widgets/tag-editor/tag-editor.js',
      'static/js/widgets/listener-editor/listener-editor.js',
      'static/js/widgets/listener-editor/security-policy-editor.js',
      'static/js/widgets/expando.js',
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
      'static/js/pages/elb-wizard/wizard.js',
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
      'static/js/jasmine-spec/spec_account.js',
      'static/js/jasmine-spec/spec_account_new.js',
      'static/js/jasmine-spec/spec_accounts.js',
      'static/js/jasmine-spec/spec_buckets.js',
      'static/js/jasmine-spec/spec_bucket_new.js',
      'static/js/jasmine-spec/spec_bucket_contents.js',
      'static/js/jasmine-spec/spec_bucket_details.js',
      'static/js/jasmine-spec/spec_bucket_item_details.js',
      'static/js/jasmine-spec/spec_bucket_upload.js',
      'static/js/jasmine-spec/spec_create_alarm.js',
      'static/js/jasmine-spec/spec_dashboard.js',
      'static/js/jasmine-spec/spec_group.js',
      'static/js/jasmine-spec/spec_groups.js',
      'static/js/jasmine-spec/spec_image.js',
      'static/js/jasmine-spec/spec_images.js',
      'static/js/jasmine-spec/spec_iam_policy_wizard.js',
      'static/js/jasmine-spec/spec_instance.js',
      'static/js/jasmine-spec/spec_instances.js',
      'static/js/jasmine-spec/spec_instance_create_ebs_image.js',
      'static/js/jasmine-spec/spec_instance_create_image.js',
      'static/js/jasmine-spec/spec_instance_launch.js',
      'static/js/jasmine-spec/spec_instance_launch_more.js',
      'static/js/jasmine-spec/spec_instance_types.js',
      'static/js/jasmine-spec/spec_instance_volumes.js',
      'static/js/jasmine-spec/spec_ipaddress.js',
      'static/js/jasmine-spec/spec_ipaddresses.js',
      'static/js/jasmine-spec/spec_landingpage.js',
      'static/js/jasmine-spec/spec_login.js',
      'static/js/jasmine-spec/spec_modal.js',
      'static/js/jasmine-spec/spec_keypair.js',
      'static/js/jasmine-spec/spec_keypairs.js',
      'static/js/jasmine-spec/spec_launchconfig.js',
      'static/js/jasmine-spec/spec_launchconfigs.js',
      'static/js/jasmine-spec/spec_launchconfig_wizard.js',
      'static/js/jasmine-spec/spec_role.js',
      'static/js/jasmine-spec/spec_roles.js',
      'static/js/jasmine-spec/spec_scalinggroup.js',
      'static/js/jasmine-spec/spec_scalinggroups.js',
      'static/js/jasmine-spec/spec_scalinggroup_instances.js',
      'static/js/jasmine-spec/spec_scalinggroup_policies.js',
      'static/js/jasmine-spec/spec_scalinggroup_wizard.js',
      'static/js/jasmine-spec/spec_securitygroup.js',
      'static/js/jasmine-spec/spec_securitygroups.js',
      'static/js/jasmine-spec/spec_snapshot.js',
      'static/js/jasmine-spec/spec_snapshots.js',
      'static/js/jasmine-spec/spec_users.js',
      'static/js/jasmine-spec/spec_user_new.js',
      'static/js/jasmine-spec/spec_user_view.js',
      'static/js/jasmine-spec/spec_user_view_update.js',
      'static/js/jasmine-spec/spec_user_view_password.js',
      'static/js/jasmine-spec/spec_user_view_accesskeys.js',
      'static/js/jasmine-spec/spec_user_view_groups.js',
      'static/js/jasmine-spec/spec_user_view_quotas.js',
      'static/js/jasmine-spec/spec_volume.js',
      'static/js/jasmine-spec/spec_volumes.js',
      'static/js/jasmine-spec/spec_volume_snapshots.js',
      'static/js/jasmine-spec/listener-editor/spec_listener_editor.js',
      'static/js/jasmine-spec/elb-wizard/spec_elb_wizard.js',
      'static/js/jasmine-spec/tag-editor/spec_tag_editor.js'
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
