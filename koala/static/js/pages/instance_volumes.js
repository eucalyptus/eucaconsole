/**
 * @fileOverview Instance Volumes page JS
 * @requires AngularJS
 *
 */

angular.module('InstanceVolumes', [])
    .controller('InstanceVolumesCtrl', function ($scope, $http, $timeout) {
        // Volume states are: "attached", "attaching", "detaching"
        // 'detached' state doesn't apply here since it won't be attached to the instance
        $scope.transitionalStates = ['attaching', 'detaching'];
        $scope.loading = false;
        $scope.volumes = [];
        $scope.jsonEndpoint = '';
        $scope.initialLoading = true;
        $scope.isTransitional = function (state) {
            return $scope.transitionalStates.indexOf(state) !== -1;
        };
        $scope.initController = function (jsonEndpoint) {
            $scope.jsonEndpoint = jsonEndpoint;
            $scope.initChosenSelector();
            $scope.getInstanceVolumes();
        };
        $scope.initChosenSelector = function () {
            $(document).ready(function() {
                $('#attach-volume-modal').on('open', function() {
                    $('#volume_id').chosen({'width': '75%'});
                });
            });
        };
        $scope.getInstanceVolumes = function () {
            $http.get($scope.jsonEndpoint).success(function(oData) {
                var transitionalVolumesCount = 0;
                $scope.volumes = oData ? oData.results : [];
                $scope.initialLoading = false;
                // Detect if any volume states are transitional
                $scope.volumes.forEach(function(volume) {
                    if ($scope.isTransitional(volume.status)) {
                        transitionalVolumesCount += 1;
                    }
                });
                // Auto-refresh volumes if any of them are transitional
                if (transitionalVolumesCount > 0) {
                    $timeout(function() {$scope.getInstanceVolumes()}, 4000);  // Poll every 4 seconds
                }
            });
        };
    })
;

