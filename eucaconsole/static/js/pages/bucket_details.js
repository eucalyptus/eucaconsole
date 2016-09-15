/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Bucket detail page JS
 * @requires AngularJS, jQuery
 *
 */

/* Bucket details page includes the S3 Sharing Panel */
angular.module('BucketDetailsPage', ['S3SharingPanel', 'EucaConsoleUtils'])
    .controller('BucketDetailsPageCtrl', function ($scope, $http, eucaHandleErrorS3, eucaUnescapeJson) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketDetailsForm = $('#bucket-details-form');
        $scope.isSubmitted = false;
        $scope.hasChangesToBeSaved = false;
        $scope.objectsCountLoading = true;
        $scope.savingCorsConfig = false;
        $scope.deletingCorsConfig = false;
        $scope.hasCorsConfig = false;
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.bucketObjectsCountUrl = options.bucket_objects_count_url;
            $scope.hasCorsConfig = options.has_cors_config;
            $scope.getBucketObjectsCount();
            $scope.handleUnsavedChanges();
            $scope.handleUnsavedSharingEntry($scope.bucketDetailsForm);
            // set upload button target based on media query
            if (Foundation.utils.is_medium_up()) {
                $('#upload-file-action').attr('target', 'upload-file');
            }
        };
        $scope.getBucketObjectsCount = function () {
            $http.get($scope.bucketObjectsCountUrl).success(function(oData) {
                var results = oData ? oData.results : {};
                $scope.bucketCount = results.object_count;
                $scope.versionCount = results.version_count;
                $scope.objectsCountLoading = false;
            }).error(function (oData, status) {
                eucaHandleErrorS3(oData, status);
            });
        };
        $scope.revealModal = function (action) {
            var modal = $('#' + action + '-modal');
            modal.foundation('reveal', 'open');
            modal.find('h3').click();  // Workaround for dropdown menu not closing
        };
        $scope.handleUnsavedChanges = function () {
            // Listen for sharing panel update
            $scope.$on('s3:sharingPanelAclUpdated', function () {
                $scope.hasChangesToBeSaved = true;
            });
            // Listen for metadata update
            $scope.$on('s3:objectMetadataUpdated', function () {
                $scope.hasChangesToBeSaved = true;
            });
            $scope.$watch('objectName', function (newVal, oldVal) {
                if (newVal !== oldVal) {
                    $scope.hasChangesToBeSaved = true;
                }
            });
            //
            $('#propagate_acls').on('change', function () {
                if ($(this).is(':checked')) {
                    $scope.hasChangesToBeSaved = true;
                }
            });
            // Turn "isSubmitted" flag to true when a form (except the logout form) is submitted
            $('form[id!="euca-logout-form"]').on('submit', function () {
                $scope.isSubmitted = true;
            });
            // Warn the user about the unsaved changes
            window.onbeforeunload = function() {
                if ($scope.hasChangesToBeSaved && !$scope.isSubmitted) {
                    return $('#warning-message-unsaved-changes').text();
                }
            };
        };
        $scope.handleUnsavedSharingEntry = function (form) {
            // Display warning when there's an unsaved Sharing Panel entry
            form.on('submit', function (event) {
                var accountInputField = form.find('#share_account:visible');
                if (accountInputField.length && accountInputField.val() !== '') {
                    event.preventDefault();
                    $scope.isSubmitted = false;
                    $('#unsaved-sharing-warning-modal').foundation('reveal', 'open');
                    return false;
                }
            });
        };
        $scope.setCorsConfiguration = function ($event, setConfigurationUrl) {
            $event.preventDefault();
            $scope.savingCorsConfig = true;
            $scope.corsError = '';
            var corsDialog = $('#cors-configuration-modal');
            var corsForm = $('#cors-configuration-form');
            var csrfToken = corsForm.find('#csrf_token').val();
            var corsTextarea = corsForm.find('textarea');
            var data = {
                'csrf_token': csrfToken,
                'cors_configuration_xml': corsTextarea.val()
            };
            $http.post(setConfigurationUrl, data).then(function successCallback(response) {
                corsDialog.foundation('reveal', 'close');
                $scope.savingCorsConfig = false;
                $scope.hasCorsConfig = true;
                Notify.success(response.data.message);
            }, function errorCallback(errData) {
                $scope.corsError = errData.data.message;
                $scope.savingCorsConfig = false;
            });
        };
        $scope.deleteCorsConfig = function ($event, deleteConfigurationUrl) {
            $event.preventDefault();
            $scope.deleteError = '';
            $scope.deletingCorsConfig = true;
            var deleteDialog = $('#cors-delete-confirmation-modal');
            var corsForm = $('#cors-deletion-form');
            var csrfToken = corsForm.find('#csrf_token').val();
            var data = {
                params: {'csrf_token': csrfToken}
            };
            $http.delete(deleteConfigurationUrl, data).then(function successCallback(response) {
                deleteDialog.foundation('reveal', 'close');
                $scope.deletingCorsConfig = false;
                $scope.hasCorsConfig = false;
                Notify.success(response.data.message);
            }, function errorCallback(errData) {
                $scope.deleteError = errData.data.message;
                $scope.deletingCorsConfig = false;
            });
        };
        // Receive postMessage from file upload window, refreshing list when file upload completes
        window.addEventListener('message', function (event) {
            if (event.data === 's3:fileUploaded') {
                $scope.getBucketObjectsCount();
            }
        }, false);
    })
;

