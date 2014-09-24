/**
 * @fileOverview Create bucket page JS
 * @requires AngularJS, jQuery
 *
 */

/* Create Bucket page includes the S3 Sharing Panel */
angular.module('CreateBucketPage', ['S3SharingPanel'])
    .controller('CreateBucketPageCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.createBucketForm = $('#create-bucket-form');
        $scope.isSubmitted = false;
        $scope.hasChangesToBeSaved = false;
        $scope.bucketName = '';
        $scope.initController = function (optionsJson) {
            var unescapedJson = optionsJson.replace(/__apos__/g, "\'").replace(/__dquote__/g, '\\"').replace(/__bslash__/g, "\\");
            var options = JSON.parse(unescapedJson);
            $scope.bucketName = options['bucket_name'];
            if (options['share_type'] == 'private') {
                $('#share_type').find('input[value="private"]').click();
            }
            $scope.handleUnsavedChanges();
            $scope.handleUnsavedSharingEntry($scope.createBucketForm);
        };
        $scope.handleUnsavedChanges = function () {
            // Listen for sharing panel update
            $scope.$on('s3:sharingPanelAclUpdated', function () {
                $scope.hasChangesToBeSaved = true;
            });
            $scope.$watch('bucketName', function (newVal) {
                if (newVal != '') {
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

