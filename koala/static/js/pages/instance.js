/**
 * @fileOverview Instance page JS
 * @requires AngularJS
 *
 */

// Instance page includes the tag editor, so pull in that module as well.
angular.module('InstancePage', ['TagEditor'])
    .controller('InstancePageCtrl', function ($scope, $http, $timeout) {
        $scope.instanceStateEndpoint = '';
        // Valid instance states are: "pending", "running", "shutting-down", "terminated", "stopping", "stopped"
        // 'shutting-down' = terminating state
        $scope.transitionalStates = ['pending', 'stopping', 'shutting-down'];
        $scope.instanceState = '';
        $scope.isUpdating = false;
        $scope.isNotStopped = $scope.instancestate != 'stopped';
        $scope.isTransitional = function (state) {
            return $scope.transitionalStates.indexOf(state) !== -1;
        };
        $scope.initController = function (jsonEndpoint, state) {
            $scope.instanceStateEndpoint = jsonEndpoint;
            $scope.instanceState = state;
            $scope.getInstanceState();
        };
        $scope.getInstanceState = function () {
            $http.get($scope.instanceStateEndpoint).success(function(oData) {
                $scope.instanceState = oData ? oData.results : '';

                // Poll to obtain desired end state if current state is transitional
                if ($scope.isTransitional($scope.instanceState)) {
                    $scope.isUpdating = true;
                    $timeout(function() {$scope.getInstanceState()}, 4000);  // Poll every 4 seconds
                } else {
                    $scope.isUpdating = false;
                }
                if ($scope.instanceState != 'stopped') {
                    $scope.isNotStopped = true;
                } else {
                    $scope.isNotStopped = false;
                }
            });
        };
    })
;

