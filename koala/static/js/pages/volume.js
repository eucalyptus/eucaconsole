/**
 * @fileOverview Volume page JS
 * @requires AngularJS
 *
 */

// Volume page includes the tag editor, so pull in that module as well.
angular.module('VolumePage', ['TagEditor'])
    .controller('VolumePageCtrl', function ($scope, $http, $timeout) {
        $scope.volumeStateEndpoint = '';
        $scope.transitionalStates = ['creating', 'deleting'];
        $scope.volumeState = '';
        $scope.isUpdating = false;
        $scope.stateIsTransitional = function (state) {
            return $scope.transitionalStates.indexOf(state) !== -1;
        };
        $scope.initChosenSelector = function () {
            $(document).ready(function() {
                $('#snapshot_id').chosen({'width': '75%'});
            });
        }
        $scope.initController = function (jsonEndpoint, state) {
            $scope.initChosenSelector();
            $scope.volumeStateEndpoint = jsonEndpoint;
            $scope.volumeState = state.replace('-', ' ');
            if (jsonEndpoint) {
                $scope.getVolumeState();
            }
        };
        $scope.getVolumeState = function () {
            $http.get($scope.volumeStateEndpoint).success(function(oData) {
                $scope.volumeState = oData ? oData.results.replace('-', ' ') : '';
                // Poll to obtain desired end state if current state is transitional
                if ($scope.stateIsTransitional($scope.volumeState)) {
                    $scope.isUpdating = true;
                    $timeout(function() {$scope.getVolumeState()}, 4000);  // Poll every 4 seconds
                } else {
                    $scope.isUpdating = false;
                }
            });
        };
    })
;

