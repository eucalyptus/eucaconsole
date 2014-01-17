/**
 * @fileOverview Scaling group Instances page JS
 * @requires AngularJS
 *
 */

angular.module('ScalingGroupInstances', [])
    .controller('ScalingGroupInstancesCtrl', function ($scope, $http) {
        $scope.loading = false;
        $scope.instances = [];
        $scope.instanceID = '';
        $scope.jsonEndpoint = '';
        $scope.initialLoading = true;
        $scope.markUnhealthyModal = $('#mark-unhealthy-modal');
        $scope.initController = function (jsonEndpoint) {
            $scope.jsonEndpoint = jsonEndpoint;
            $scope.getScalingGroupInstances();
        };
        $scope.getScalingGroupInstances = function () {
            $http.get($scope.jsonEndpoint).success(function(oData) {
                $scope.instances = oData ? oData.results : [];
                $scope.initialLoading = false;
            });
        };
        $scope.revealUnhealthyModal = function (instance) {
            $scope.instanceID = instance['id'];
            $scope.markUnhealthyModal.foundation('reveal', 'open');
        }
    })
;

