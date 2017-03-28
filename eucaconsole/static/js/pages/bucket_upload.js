/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
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
        $scope.isNotValid = true;
        $scope.files = [];
        $scope.uploading = false;
        $scope.progress = 0;
        $scope.total = 0;
        $scope.initController = function (uploadUrl, signUrl, bucketUrl) {
            $scope.uploadUrl = uploadUrl;
            $scope.signUrl = signUrl;
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
            $scope.$watchCollection('files', function (newVals) {
                $('#size-error').css('display', 'none');
                $scope.isNotValid = false;
                if (newVals.length > 0) {
                    $scope.hasChangesToBeSaved = true;
                    angular.forEach($scope.files, function(value, idx) {
                        if (value.size > 5000000000) {
                            $('#size-error').css('display', 'block');
                            $scope.isNotValid = true;
                        }
                    });
                }
            }, true);
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
            var url = $scope.signUrl + '/' + file.name;
            var data = "csrf_token="+$('#csrf_token').val();
            $http.post(url, data, {
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                }).
                success(function(oData) {
                    var results = oData ? oData.results : [];
                    console.log("upload url = "+results.url);
                    var fd = new FormData();
                    // fill from actual form
                    angular.forEach(results.fields, function(value, key) {
                        this.append(key, value);
                    }, fd);
                    fd.append('Content-Type', file.type);
                    // Add file: consider batching up lots of small files
                    fd.append('files', file);
                    $http.post(results.url, fd, {
                            transformRequest: angular.identity,
                            headers: {'Content-Type': file.type}
                        }).
                        success(function(oData) {
                            $scope.progress = $scope.progress + 1;
                            if ($scope.progress == $scope.total) {
                                var parentWindow = window.opener;
                                $('#upload-files-modal').foundation('reveal', 'close');
                                $scope.hasChangesToBeSaved = false;
                                if (parentWindow) {
                                    parentWindow.postMessage('s3:fileUploaded', '*');
                                }
                                $scope.cancel();
                            }
                            if ($scope.uploading === true) {
                                $scope.uploadFile();
                            }
                        }).
                        error(function(oData, status) {
                            $('#upload-files-modal').foundation('reveal', 'close');
                            $scope.uploading = false;
                            $scope.progress = 0;
                            Notify.failure(oData.message);
                        });
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
            $scope.cancel();
        };
        $scope.cancel = function () {
            if (Foundation.utils.is_medium_up()) {
                window.close();
            }
            else {
                window.location = $scope.bucketUrl;
            }
        };
    })
;

