/**
 * @fileOverview Instance page JS
 * @requires AngularJS
 *
 */

// Instance page includes the tag editor, so pull in that module as well.
angular.module('InstancePage', ['TagEditor'])
    .controller('InstancePageCtrl', function ($scope, $http, $timeout) {
        $scope.instanceStateEndpoint = '';
        $scope.transitionalStates = ['pending', 'stopping', 'shutting-down'];
        $scope.instanceState = '';
        $scope.isUpdating = false;
        $scope.stateIsTransitional = function (state) {
            return $scope.transitionalStates.indexOf(state) !== -1;
        };
        $scope.initController = function (jsonEndpoint, state) {
            $scope.instanceStateEndpoint = jsonEndpoint;
            $scope.instanceState = state;
            $scope.getInstanceState();
        };
        $scope.getInstanceState = function () {
            $scope.isUpdating = true;
            $http.get($scope.instanceStateEndpoint).success(function(oData) {
                $scope.instanceState = oData ? oData.results : '';
                // Poll to obtain desired end state if current state is transitional
                if ($scope.stateIsTransitional($scope.instanceState)) {
                    $timeout(function() {$scope.getInstanceState()}, 5000);  // Poll every 5 seconds
                } else {
                    $scope.isUpdating = false;
                }
            });
        };
    })
;

