/**
 * @fileOverview Block Device Mapping Editor JS
 * @requires AngularJS
 *
 */
angular.module('BlockDeviceMappingEditor', [])
    .controller('BlockDeviceMappingEditorCtrl', function ($scope) {
        $scope.bdmTextarea = $('#bdmapping');
        $scope.bdMapping = {};
        $scope.ephemeralCount = 0;
        $scope.setInitialNewValues = function () {
            $scope.newVolumeType = 'EBS';
            $scope.newSnapshotID = '';
            $scope.newMappingPath = '';
            $scope.newSize = '2';
            $scope.newDOT = true;
        };
        $scope.initChosenSelector = function () {
            $('#new-blockdevice-entry').find('select[name="snapshot_id"]').chosen({'width': '100%'});
        };
        $scope.initBlockDeviceMappingEditor = function (bdmJson) {
            bdmJson = bdmJson || "{}";
            $scope.bdMapping = JSON.parse(bdmJson);
            $scope.bdmTextarea.val(bdmJson);
            $scope.setInitialNewValues();
            $scope.initChosenSelector();
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
            if ($scope.newVolumeType === 'ephemeral') {
                $scope.ephemeralCount += 1;
            }
            $scope.setInitialNewValues();  // Reset values
            newMappingEntry.focus();
        };
        $scope.removeDevice = function (key) {
            var bdMapping = $scope.bdMapping;
            delete bdMapping[key];
            $scope.bdmTextarea.val(JSON.stringify(bdMapping));
        };
        $scope.updateRootDevice = function (key, $event) {
            var bdMappingText = $scope.bdmTextarea.val();
            if (bdMappingText && key == '/dev/sda1') {
                var bdMapping = JSON.parse(bdMappingText);
                var rootDevice = bdMapping['/dev/sda1'] || '';
                if (rootDevice) {
                    bdMapping[key]['size'] = parseInt($($event.target).val(), 10);
                    $scope.bdmTextarea.val(JSON.stringify(bdMapping));
                }
            }
        };
    })
;
