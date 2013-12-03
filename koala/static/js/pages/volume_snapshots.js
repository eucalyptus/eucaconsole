/**
 * @fileOverview Volume Snapshots page JS
 * @requires AngularJS
 *
 */

angular.module('VolumeSnapshots', [])
    .controller('VolumeSnapshotsCtrl', function ($scope, $http, $timeout) {
        $scope.loading = false;
        $scope.snapshots = [];
        $scope.jsonEndpoint = '';
        $scope.initialLoading = true;
        $scope.initController = function (jsonEndpoint) {
            $scope.jsonEndpoint = jsonEndpoint;
            $scope.getVolumeSnapshots();
        };
        $scope.getVolumeSnapshots = function () {
            $http.get($scope.jsonEndpoint).success(function(oData) {
                var inProgressCount = 0;
                $scope.snapshots = oData ? oData.results : [];
                $scope.initialLoading = false;
                // Detect if any snapshots are in progress
                $scope.snapshots.forEach(function(snapshot) {
                    var progress = parseInt(snapshot.progress.replace('%', ''), 10);
                    if (progress < 100) {
                        inProgressCount += 1;
                    }
                });
                // Auto-refresh snapshots if any of them are in progress
                if (inProgressCount > 0) {
                    $timeout(function() {$scope.getVolumeSnapshots()}, 4000);  // Poll every 4 seconds
                }
            });
        };
    })
;

