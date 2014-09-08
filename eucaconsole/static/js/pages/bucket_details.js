/**
 * @fileOverview Bucket detail page JS
 * @requires AngularJS, jQuery
 *
 */

/* Bucket details page includes the S3 Sharing Panel */
angular.module('BucketDetailsPage', ['S3SharingPanel'])
    .controller('BucketDetailsPageCtrl', function ($scope, $http) {
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
        };
        $scope.getBucketObjectsCount = function () {
            $http.get($scope.bucketObjectsCountUrl).success(function(oData) {
                var results = oData ? oData.results : {};
                $scope.bucketCount = results['object_count'];
                $scope.objectsCountLoading = false;
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
                if (errorMsg) {
                    if (status === 403 || status === 400) {
                        $('#timed-out-modal').foundation('reveal', 'open');
                    } else {
                        Notify.failure(errorMsg);
                    }
                }
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
    })
;

