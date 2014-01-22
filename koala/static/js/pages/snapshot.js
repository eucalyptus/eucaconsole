/**
 * @fileOverview Snapshot detail page JS
 * @requires AngularJS
 *
 */

// Snapshot page includes the tag editor, so pull in that module as well.
angular.module('SnapshotPage', ['TagEditor'])
    .controller('SnapshotPageCtrl', function ($scope, $http, $timeout) {
        $scope.snapshotStatusEndpoint = '';
        $scope.transitionalStates = ['pending', 'deleting'];
        $scope.snapshotStatus = '';
        $scope.snapshotProgress = '';
        $scope.isUpdating = false;
        $scope.isTransitional = function (state) {
            return $scope.transitionalStates.indexOf(state) !== -1;
        };
        $scope.inProgress = function (progress) {
            progress = parseInt(progress.replace('%', ''), 10);
            return progress < 100
        };
        $scope.initChosenSelector = function () {
            $(document).ready(function() {
                $('#volume_id').chosen({'width': '75%', search_contains: true});
                if ($('#volume_id').children().length == 1) {
                    var modal = $('#create-warn-modal');
                    modal.foundation('reveal', 'open');
                }
            });
        }
        $scope.initController = function (jsonEndpoint, status, progress) {
            $scope.initChosenSelector();
            $scope.snapshotStatusEndpoint = jsonEndpoint;
            $scope.snapshotStatus = status;
            $scope.snapshotProgress = progress;
            if (jsonEndpoint) {
                $scope.getSnapshotState();
            }
        };
        $scope.getSnapshotState = function () {
            $http.get($scope.snapshotStatusEndpoint).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $scope.snapshotStatus = results['status'];
                    $scope.snapshotProgress = results['progress'];
                    // Poll to obtain desired end state if current state is transitional or snapshot is in progress
                    if ($scope.isTransitional($scope.snapshotStatus) || $scope.inProgress($scope.snapshotProgress)) {
                        $scope.isUpdating = true;
                        $timeout(function() {$scope.getSnapshotState()}, 5000);  // Poll every 5 seconds
                    } else {
                        $scope.isUpdating = false;
                    }
                }
            });
        };
    })
;

