/**
 * @fileOverview Buckets landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('BucketsPage', ['LandingPage'])
    .controller('BucketsCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketName = '';
        $scope.updateVersioningAction = '';
        $scope.bucketCounts = {};
        $scope.countsLoading = {};
        $scope.initController = function (bucketObjectsCountUrl, updateVersioningFormUrl) {
            $scope.bucketObjectsCountUrl = bucketObjectsCountUrl;
            $scope.updateVersioningFormUrl = updateVersioningFormUrl;
        };
        $scope.revealModal = function (action, bucket) {
            var modal = $('#' + action + '-modal');
            $scope.bucketName = bucket['bucket_name'];
            $scope.updateVersioningAction = bucket['update_versioning_action'];
            modal.on('opened', function () {
                // Set form action based on bucket choice
                modal.find('form').attr('action', $scope.updateVersioningFormUrl.replace('_name_', $scope.bucketName));
            });
            modal.foundation('reveal', 'open');
        };
        $scope.$on('itemsLoaded', function($event, items) {
            angular.forEach(items, function(item, key) {
                var bucketName = item['bucket_name'];
                var objectsCountUrl = $scope.bucketObjectsCountUrl.replace('_name_', bucketName);
                $scope.countsLoading[bucketName] = true;
                $http.get(objectsCountUrl).success(function(oData) {
                    var results = oData ? oData.results : {};
                    $scope.bucketCounts[bucketName] = results['object_count'];
                    $scope.countsLoading[bucketName] = false;
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
            });
        });
    })
;

