/**
 * @fileOverview Upload file page JS
 * @requires AngularJS, jQuery
 *
 */

/* Upload File page includes the S3 Sharing Panel */
angular.module('UploadFilePage', ['S3SharingPanel', 'S3MetadataEditor'])
    .directive('file', function(){
        return {
            restrict: 'A',
            link: function($scope, el, attrs){
                el.bind('change', function(event){
                    $scope.files = event.target.files;
                    $scope.$apply();
                });
            }
        };
    })
    .controller('UploadFilePageCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.createBucketForm = $('#create-bucket-form');
        $scope.isSubmitted = false;
        $scope.hasChangesToBeSaved = false;
        $scope.files = [];
        $scope.uploading = false;
        $scope.progress = 0;
        $scope.total = 0;
        $scope.initController = function (uploadUrl, bucketUrl) {
            $scope.uploadUrl = uploadUrl;
            $scope.bucketUrl = bucketUrl;
            $scope.handleUnsavedChanges();
            $scope.handleUnsavedSharingEntry($scope.createBucketForm);
        };
        $scope.toggleAdvContent = function () {
            $scope.adv_expanded = !$scope.adv_expanded;
        };
        $scope.handleUnsavedChanges = function () {
            // Listen for sharing panel update
            $scope.$on('s3:sharingPanelAclUpdated', function () {
                $scope.hasChangesToBeSaved = true;
            });
            $scope.$watch('files', function (newVals) {
                if (newVals.length > 0) {
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
        $scope.startUpload = function($event) {
            $event.preventDefault();
            $('#upload-files-modal').foundation('reveal', 'open');
            $scope.uploading = true;
            $scope.progress = 0;
            $scope.total = $scope.files.length;
            $scope.uploadFile();
        };
        $scope.uploadFile = function($event) {
            var file = $scope.files[$scope.progress];
            var fd = new FormData()
            // fill from actual form
            angular.forEach($('form').serializeArray(), function(value, key) {
                this.append(value.name, value.value);
            }, fd);
            // Add file: consider batching up lots of small files
            fd.append('files', file);
            var url = $scope.uploadUrl + '/' + file.name;
            $http.post(url, fd, {
                    headers: {'Content-Type': undefined},
                    transformRequest: angular.identity,
                  }).
                success(function(oData) {
                    $scope.progress = $scope.progress + 1;
                    if ($scope.progress == $scope.total) {
                        $('#upload-files-modal').foundation('reveal', 'close');
                        $scope.hasChangesToBeSaved = false;
                        $scope.cancel()
                    }
                    if ($scope.uploading == true) {
                        $scope.uploadFile();
                    }
                }).
                error(function(oData, status) {
                    $('#upload-files-modal').foundation('reveal', 'close');
                    $scope.uploading = false;
                    $scope.progress = 0;
                    Notify.failure(oData.message);
                });
        };
        $scope.cancelUploading = function () {
            $('#upload-files-modal').foundation('reveal', 'close');
            $scope.uploading = false;
            $scope.progress = 0;
            $scope.hasChangesToBeSaved = false;
            $scope.cancel()
        };
        $scope.cancel = function () {
            if (window.matchMedia(Foundation.media_queries['small']).matches === false) {
                window.close()
            }
            else {
                window.location = $scope.bucketUrl;
            }
        };
    })
;

