/**
 * @fileOverview Bucket item (folder/object) detail page JS
 * @requires AngularJS, jQuery
 *
 */

/* Bucket item details page includes the S3 Sharing Panel and Metadata Editor */
angular.module('BucketItemDetailsPage', ['S3SharingPanel', 'S3MetadataEditor'])
    .controller('BucketItemDetailsPageCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.saveChangesBtnDisabled = true;
        $scope.objectName = '';
        $scope.initController = function () {
            $scope.setInitialValues();
            $scope.addListeners();
        };
        $scope.setInitialValues = function () {
            $scope.objectName = $('#friendly_name').val();
        };
        $scope.addListeners = function () {
            // Listen for sharing panel update
            $scope.$on('s3:sharingPanelAclUpdated', function () {
                $scope.saveChangesBtnDisabled = false;
            });
            // Listen for metadata update
            $scope.$on('s3:objectMetadataUpdated', function () {
                $scope.saveChangesBtnDisabled = false;
            });
            $scope.$watch('objectName', function (newVal, oldVal) {
                if (newVal != oldVal) {
                    $scope.saveChangesBtnDisabled = false;
                }
            });
        }
    })
;

