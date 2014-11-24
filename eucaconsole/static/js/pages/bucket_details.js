/**
 * @fileOverview Bucket detail page JS
 * @requires AngularJS, jQuery
 *
 */

/* Bucket details page includes the S3 Sharing Panel */
angular.module('BucketDetailsPage', ['S3SharingPanel', 'EucaConsoleUtils'])
    .controller('BucketDetailsPageCtrl', function ($scope, $http, eucaHandleErrorS3) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketDetailsForm = $('#bucket-details-form');
        $scope.isSubmitted = false;
        $scope.hasChangesToBeSaved = false;
        $scope.objectsCountLoading = true;
        $scope.initController = function (bucketObjectsCountUrl) {
            $scope.bucketObjectsCountUrl = bucketObjectsCountUrl;
            $scope.getBucketObjectsCount();
            $scope.handleUnsavedChanges();
            $scope.handleUnsavedSharingEntry($scope.bucketDetailsForm);
            // set upload button target based on media query
            if (window.matchMedia(Foundation.media_queries['small']).matches === false) {
                $('#upload-file-action').attr('target', '_blank');
            }
        };
        $scope.getBucketObjectsCount = function () {
            $http.get($scope.bucketObjectsCountUrl).success(function(oData) {
                var results = oData ? oData.results : {};
                $scope.bucketCount = results['object_count'];
                $scope.versionCount = results['version_count'];
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
                if (newVal != oldVal) {
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
                if (accountInputField.length && accountInputField.val() != '') {
                    event.preventDefault();
                    $scope.isSubmitted = false;
                    $('#unsaved-sharing-warning-modal').foundation('reveal', 'open');
                    return false;
                }
            });
        };
    })
;

