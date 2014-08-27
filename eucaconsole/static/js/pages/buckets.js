/**
 * @fileOverview Buckets landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('BucketsPage', ['LandingPage'])
    .controller('BucketsCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketName = '';
        $scope.bucketCounts = {};
        $scope.countsLoading = true;
        $scope.initController = function (bucketsObjectCountsUrl) {
            $scope.bucketsObjectCountsUrl = bucketsObjectCountsUrl;
        };
        $scope.revealModal = function (action, bucket) {
            var modal = $('#' + action + '-bucket-modal');
            $scope.bucketName = bucket['name'];
            modal.foundation('reveal', 'open');
        };
        $scope.$on('itemsLoaded', function($event, items) {
            $http.get($scope.bucketsObjectCountsUrl).success(function(oData) {
                var results = oData ? oData.results : {};
                angular.forEach(results, function(item, key) {
                    $scope.bucketCounts[item.bucket_name] = item.object_count;
                });
                $scope.countsLoading = false;
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
            });
        });
    })
;

