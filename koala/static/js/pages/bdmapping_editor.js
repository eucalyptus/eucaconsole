/**
 * @fileOverview Block Device Mapping Editor JS
 * @requires AngularJS
 *
 */
angular.module('BlockDeviceMappingEditor', [])
    .controller('BlockDeviceMappingEditorCtrl', function ($scope) {
        $scope.bdmTextarea = $('#bdmapping');
        $scope.bdMapping = {};
        $scope.setInitialNewValues = function () {
            $scope.newVolumeType = 'EBS';
            $scope.newSnapshotID = '';
            $scope.newMappingPath = '';
            $scope.newSize = '2';
            $scope.newDOT = true;
        };
        $scope.initBlockDeviceMappingEditor = function (bdmJson) {
            bdmJson = bdmJson || "{}";
            $scope.bdMapping = JSON.parse(bdmJson);
            $scope.bdmTextarea.val(bdmJson);
            $scope.setInitialNewValues();
        };
        $scope.addDevice = function () {
            // Validation checks
            var newMappingEntry = $('#new-mapping-path'),
                newSizeEntry = $('#new-size');
            // Be sure a mapping path is entered
            if (!newMappingEntry.val()) {
                newMappingEntry.focus();
                return false;
            }
            // Size must be entered
            if (!newSizeEntry.val()) {
                newSizeEntry.focus();
                return false;
            }
            var bdMapping = $scope.bdMapping;
            bdMapping[$scope.newMappingPath] = {
                'volume_type': $scope.newVolumeType,
                'snapshot_id': $scope.newSnapshotID,
                'size': $scope.newSize,
                'delete_on_termination': $scope.newDOT
            };
            $scope.bdmTextarea.val(JSON.stringify(bdMapping));
            $scope.setInitialNewValues();  // Reset values
        };
        $scope.removeDevice = function (key) {
            var bdMapping = $scope.bdMapping;
            delete bdMapping[key];
            $scope.bdmTextarea.val(JSON.stringify(bdMapping));
        }
    })
;
