/**
 * @fileOverview Bucket item (folder/object) detail page JS
 * @requires AngularJS, jQuery
 *
 */

/* Bucket item details page includes the S3 Sharing Panel and Metadata Editor */
angular.module('BucketItemDetailsPage', ['S3SharingPanel', 'S3MetadataEditor'])
    .controller('BucketItemDetailsPageCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketItemDetailsForm = $('#bucket-item-details-form');
        $scope.isSubmitted = false;
        $scope.hasChangesToBeSaved = false;
        $scope.objectName = '';
        $scope.initController = function () {
            $scope.setInitialValues();
            $scope.handleUnsavedChanges();
            $scope.handleUnsavedSharingEntry($scope.bucketItemDetailsForm);
            $scope.handleUnsavedMetadataEntry($scope.bucketItemDetailsForm);
        };
        $scope.setInitialValues = function () {
            $scope.objectName = $('#friendly_name').val();
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
                if (newVal != oldVal) {
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
                var accountInputField = form.find('#share_account');
                if (accountInputField.length && accountInputField.val() != '') {
                    event.preventDefault();
                    $scope.isSubmitted = false;
                    $('#unsaved-sharing-warning-modal').foundation('reveal', 'open');
                    return false;
                }
            });
        };
        $scope.handleUnsavedMetadataEntry = function (form) {
            // Display warning when there's an unsaved Metadata Pair entry
            form.on('submit', function (event) {
                var metadataKeyInputField = form.find('#metadata_key');
                if (metadataKeyInputField.length && metadataKeyInputField.val() != '') {
                    event.preventDefault();
                    $scope.isSubmitted = false;
                    $('#unsaved-metadata-warning-modal').foundation('reveal', 'open');
                    return false;
                }
            });
        };
    })
;

