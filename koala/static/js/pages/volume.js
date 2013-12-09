/**
 * @fileOverview Volume page JS
 * @requires AngularJS
 *
 */

// Volume page includes the tag editor, so pull in that module as well.
angular.module('VolumePage', ['TagEditor'])
    .controller('VolumePageCtrl', function ($scope, $http, $timeout) {
        $scope.volumeStatusEndpoint = '';
        $scope.transitionalStates = ['creating', 'deleting', 'attaching', 'detaching'];
        $scope.volumeStatus = '';
        $scope.volumeAttachStatus = '';
        $scope.snapshotId = '';
        $scope.isUpdating = false;
        $scope.fromSnapshot = false;
        $scope.isTransitional = function (state) {
            return $scope.transitionalStates.indexOf(state) !== -1;
        };
        $scope.populateVolumeSize = function () {
            var snapshotOptionText = $('#snapshot_id').find('option[value="' + $scope.snapshotId + '"]').text(),
                snapshotSize = '';
            if (snapshotOptionText !== 'None') {
                snapshotSize = /(?:\(\d+\sGB\))/.exec(snapshotOptionText)[0].replace(/[^\d]/g, '');
                $('input#size').val(snapshotSize);
            }
        };
        $scope.initChosenSelectors = function () {
            var urlParams = $.url().param(),
                snapshotField = $('#snapshot_id');
            if (urlParams['from_snapshot']) {  // Pre-populate snapshot if passed in query string arg
                $scope.fromSnapshot = true;
                snapshotField.val(urlParams['from_snapshot']);
                $scope.snapshotId = urlParams['from_snapshot'];
                $scope.populateVolumeSize();
            }
            snapshotField.chosen({'width': '75%'});
            // Instance choices in "Attach to instance" modal dialog
            $('#attach-modal').foundation('reveal', {
                'opened': function() {
                    $('#instance_id').chosen({'width': '100%'});
                }
            });
        };
        $scope.initController = function (jsonEndpoint, status, attachStatus) {
            $scope.initChosenSelectors();
            $scope.volumeStatusEndpoint = jsonEndpoint;
            $scope.volumeStatus = status.replace('-', ' ');
            $scope.volumeAttachStatus = attachStatus;
            if (jsonEndpoint) {
                $scope.getVolumeState();
            }
        };
        $scope.getVolumeState = function () {
            $http.get($scope.volumeStatusEndpoint).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $scope.volumeStatus = results['volume_status'];
                    $scope.volumeAttachStatus = results['attach_status'];
                    // Poll to obtain desired end state if current state is transitional
                    if ($scope.isTransitional($scope.volumeStatus) || $scope.isTransitional($scope.volumeAttachStatus)) {
                        $scope.isUpdating = true;
                        $timeout(function() {$scope.getVolumeState()}, 4000);  // Poll every 4 seconds
                    } else {
                        $scope.isUpdating = false;
                    }
                }
            });
        };
    })
;

