/**
 * @fileOverview Upload file page JS
 * @requires AngularJS, jQuery
 *
 */

/* Upload File page includes the S3 Sharing Panel */
angular.module('UploadFilePage', ['S3SharingPanel'])
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
        $scope.initController = function (uploadUrl, signUrl) {
            $scope.uploadUrl = uploadUrl;
            $scope.signUrl = signUrl;
            $scope.handleUnsavedChanges();
            $scope.handleUnsavedSharingEntry($scope.createBucketForm);
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
                var accountInputField = form.find('#share_account');
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
            var data = "csrf_token="+$('#csrf_token').val();
            for (var i=0; i<$scope.files.length; i++) {
                var file = $scope.files[i];
                console.log("upload file = "+file.size+" size: "+file.size);
                // file.name
                // file.path
                // file.size
                // file.type
                var url = $scope.signUrl + '/' + file.name;
                $http({method:'POST', url:url, data:data,
                       headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                  success(function(oData) {
                    var results = oData ? oData.results : [];
                    console.log("upload url = "+results.url);
                    var fd = new FormData()
                    angular.forEach(results.fields, function(value, key) {
                        this.append(key, value);
                    }, fd);
                    fd.append('csrf_token', $('#csrf_token').val());
                    fd.append('file', file);
                    var url = $scope.uploadUrl + '/' + file.name;
                    $http.post(url, fd, {
                            headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                          }).
                        success(function(oData) {
                            Notify.success("uploaded file: "+file.name);
                        }).
                        error(function(oData, status) {
                            Notify.failure("S3 returned status: "+status);
                        });
                  }).
                  error(function (oData, status) {
                    var errorMsg = oData['message'] || '';
                    Notify.failure(errorMsg);
                  });
                console.log("file = "+file);
            }
        };
    })
;

