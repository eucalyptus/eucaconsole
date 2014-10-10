/**
 * @fileOverview Create bucket page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('CreateBucketPage', ['EucaConsoleUtils'])
    .controller('CreateBucketPageCtrl', function ($scope, $http, eucaUnescapeJson) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.createBucketForm = $('#create-bucket-form');
        $scope.isSubmitted = false;
        $scope.hasChangesToBeSaved = false;
        $scope.bucketName = '';
        $scope.existingBuckets = [];
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.bucketName = options['bucket_name'];
            $scope.existingBuckets = options['existing_bucket_names'];
            if (options['share_type'] == 'private') {
                $('#share_type').find('input[value="private"]').click();
            }
            $scope.initNameConflictWarningListener();
            $scope.handleUnsavedChanges();
        };
        $scope.handleUnsavedChanges = function () {
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
        $scope.confirmWarning = function () {
            var modal = $('#conflict-warn-modal');
            modal.foundation('reveal', 'close');
        };
        $scope.initNameConflictWarningListener = function () {
            $scope.createBucketForm.on('submit', function(evt) {
                var bucketName = $('#bucket_name').val();
                if ($scope.existingBuckets.indexOf(bucketName) !== -1) {
                    evt.preventDefault();
                    $('#conflict-warn-modal').foundation('reveal', 'open');
                }
            });
        };
    })
;

