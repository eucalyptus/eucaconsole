/**
 * @fileOverview Scaling group Instances page JS
 * @requires AngularJS
 *
 */

angular.module('ScalingGroupInstances', [])
    .controller('ScalingGroupInstancesCtrl', function ($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.loading = false;
        $scope.items = [];
        $scope.instanceID = '';
        $scope.jsonEndpoint = '';
        $scope.initialLoading = true;
        $scope.markUnhealthyModal = $('#mark-unhealthy-modal');
        $scope.initController = function (jsonEndpoint) {
            $scope.jsonEndpoint = jsonEndpoint;
            $scope.getItems();
        };
        $scope.getItems = function () {
            $http.get($scope.jsonEndpoint).success(function(oData) {
                var transitionalCount = 0;
                $scope.items = oData ? oData.results : [];
                $scope.initialLoading = false;
                $scope.items.forEach(function (item) {
                    if (item['transitional']) {
                        transitionalCount += 1;
                    }
                });
                // Auto-refresh instances if any of them are in transition
                if (transitionalCount > 0) {
                    $timeout(function() { $scope.getItems(); }, 5000);  // Poll every 5 seconds
                }
            }).error(function (oData, status) {
                var errorMsg = oData['error'] || null;
                if (errorMsg && status === 403) {
                    alert(errorMsg);
                    $('#euca-logout-form').submit();
                }
            });
        };
        $scope.revealUnhealthyModal = function (instance) {
            $scope.instanceID = instance['id'];
            $scope.markUnhealthyModal.foundation('reveal', 'open');
        }
    })
;

