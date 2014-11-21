/**
 * @fileOverview Bucket item (folder/object) detail page JS
 * @requires AngularJS, jQuery
 *
 */

/* Bucket item details page includes the S3 Sharing Panel and Metadata Editor */
angular.module('BucketItemDetailsPage', ['S3SharingPanel', 'S3MetadataEditor', 'EucaConsoleUtils'])
    .controller('BucketItemDetailsPageCtrl', function ($scope, $http, eucaUnescapeJson, eucaHandleErrorS3) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketItemDetailsForm = $('#bucket-item-details-form');
        $scope.isSubmitted = false;
        $scope.hasChangesToBeSaved = false;
        $scope.objectName = '';
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.deleteUrl = options['delete_keys_url'];
            $scope.bucketUrl = options['bucket_url'];
            $scope.bucketItemKey = options['bucket_item_key'];
            $scope.unprefixedKey = options['unprefixed_key'];
            $scope.makeObjectPublicUrl = options['make_object_public_url'];
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
                var accountInputField = form.find('#share_account:visible');
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
        $scope.saveKey = function (bucket_name, bucket_item) {
            $('.actions-menu').trigger('click');
            Modernizr.sessionstorage && sessionStorage.setItem('copy-object-buffer', bucket_name + '/' + bucket_item.name);
        };
        $scope.confirmDelete = function (name) {
            $('.actions-menu').trigger('click');
            $scope.obj_key = name;
            $('#delete-object-modal').foundation('reveal', 'open');
        };
        $scope.deleteObject = function () {
            var data = "csrf_token=" + $('#csrf_token').val() + "&keys=" + $scope.key;
            $http({method: 'POST', url: $scope.deleteUrl, data: data,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                success(function (oData) {
                    if (oData.errors !== undefined) {
                        console.log('error deleting some keys ' + oData.errors);
                    }
                    $('#delete-object-modal').foundation('reveal', 'close');
                    Notify.success(oData.message);
                    window.location = $scope.bucketUrl;
                }).
                error(function (oData, status) {
                    var errorMsg = oData['message'] || '';
                    if (errorMsg && status === 403) {
                        $('#timed-out-modal').foundation('reveal', 'open');
                    }
                    Notify.failure(errorMsg);
                });
        };
        $scope.confirmMakePublic = function () {
            $('.actions-menu').trigger('click');
            $scope.obj_key = $scope.unprefixedKey;
            $('#make-object-public-modal').foundation('reveal', 'open');
        };
        $scope.makeObjectPublic = function () {
            var data = "csrf_token=" + $('#csrf_token').val() + "&key=" + $scope.bucketItemKey + "&detailpage=1";
            $http({method: 'POST', url: $scope.makeObjectPublicUrl, data: data,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                success(function (oData) {
                    if (oData.errors !== undefined) {
                        console.log('Error making object public ' + oData.errors);
                    }
                    $('#make-object-public-modal').foundation('reveal', 'close');
                    // NOTE: We're forcing a reload here to refresh the ACLs in the sharing panel
                    // The view will send the success notice via the session, displaying the notice after page reload
                    window.location.reload();
                }).
                error(function (oData, status) {
                    eucaHandleErrorS3(oData, status);
                });
        };
    })
;

