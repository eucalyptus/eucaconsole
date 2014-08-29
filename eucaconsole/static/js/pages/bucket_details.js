/**
 * @fileOverview Bucket detail page JS
 * @requires AngularJS, jQuery
 *
 */

/* Bucket details page includes the S3 Sharing Panel */
angular.module('BucketDetailsPage', ['S3SharingPanel'])
    .controller('BucketDetailsPageCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.objectsCountLoading = true;
        $scope.initController = function (bucketObjectsCountUrl) {
            $scope.bucketObjectsCountUrl = bucketObjectsCountUrl;
            $scope.getBucketObjectsCount();
        };
        $scope.getBucketObjectsCount = function () {
            $http.get($scope.bucketObjectsCountUrl).success(function(oData) {
                var results = oData ? oData.results : {};
                $scope.bucketObjectsCount = results['object_count'];
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
        }
    })
;

