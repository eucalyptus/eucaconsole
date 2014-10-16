/**
 * @fileOverview Block Device Mapping Editor JS
 * @requires AngularJS
 *
 */
angular.module('BlockDeviceMappingEditor', ['EucaConsoleUtils'])
    .controller('BlockDeviceMappingEditorCtrl', function ($scope, $http, $timeout, eucaUnescapeJson) {
        $scope.bdmTextarea = $('#bdmapping');
        $scope.bdMapping = undefined;
        $scope.ephemeralCount = 0;
        $scope.isNotValid = true;
        $scope.snapshotJsonURL = '';
        $scope.setInitialNewValues = function () {
            $scope.newVolumeType = 'EBS';
            $scope.virtualName = '';
            $scope.newSnapshotID = '';
            $scope.newMappingPath = '';
            $scope.newSize = '2';
            $scope.newDOT = true;
            $scope.$watch('newMappingPath', function () {
                $scope.checkValidInput();
            });
            $scope.$watch('newSnapshotID', function () {
                // populate size from snapshot size
                if ($scope.newSnapshotID == '') return;
                var url = $scope.snapshotJsonURL.replace('_id_', $scope.newSnapshotID);
                var data = "csrf_token="+$('#csrf_token').val();
                $http({method:'GET', url:url, data:data,
                       headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                  success(function(oData) {
                    var results = oData ? oData.results : [];
                    if (oData.error == undefined) {
                        $scope.newSize = results;
                    } else {
                        Notify.failure(oData.message);
                    }
                  }).
                  error(function (oData, status) {
                    var errorMsg = oData['message'] || '';
                    Notify.failure(errorMsg);
                  });
            });
            $scope.$watch('newSize', function () {
                $scope.checkValidInput();
            });
        };
        $scope.checkValidInput = function () {
            if ($scope.newMappingPath == '' || $scope.newSize == '') {
                $scope.isNotValid = true;
            } else {
                $scope.isNotValid = false;
            }
        };
        $scope.initChosenSelector = function () {
            $scope.newSnapshotID = '';
            var select = $('#new-blockdevice-entry').find('select[name="snapshot_id"]')
            if (select.length > 0) {
                select.chosen({'width': '100%'});
            }
            $scope.cleanupSelections();
        };
        $scope.cleanupSelections = function () {
            // Timeout is needed to remove the empty option inject issue caused by Angular
            $timeout( function(){
                var snapshotSelector = $('#new-blockdevice-entry').find('select[name="snapshot_id"]');
                if( snapshotSelector.children('option').first().html() == '' ){
                    snapshotSelector.children('option').first().remove();
                } 
            }, 250);
        };
        // tempate-ed way to pass bdm in
        $scope.initBlockDeviceMappingEditor = function (bdmJson, url) {
            if (bdmJson != '{}') {
                $scope.bdMapping = JSON.parse(bdmJson);
            } else {
                $scope.bdMapping = undefined;
            }
            $scope.bdmTextarea.val(bdmJson);
            $scope.setInitialNewValues();
            $scope.initChosenSelector();
            $scope.snapshotJsonURL = url;
        };
        // live update of bdm json
        $scope.$on('setBDM', function($event, bdm) {
            if ($.isEmptyObject(bdm)) {
                $scope.bdMapping = undefined;
            } else {
                $scope.bdMapping = bdm;
            }
            $scope.bdmTextarea.val(JSON.stringify(bdm));
            $scope.setInitialNewValues();
            $scope.initChosenSelector();
        });
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
            if (!newSizeEntry.val() || newSizeEntry.val() <= 0) {
                newSizeEntry.focus();
                return false;
            }
            if ($scope.newVolumeType === 'ephemeral') {
                $scope.virtualName = "ephemeral" + $scope.ephemeralCount; 
                $scope.ephemeralCount += 1;
                $scope.newSnapshotID = '';
                $scope.newSize = '2';
                $scope.newDOT = false;
            }
            var bdMapping = $scope.bdMapping;
            bdMapping[$scope.newMappingPath] = {
                'virtual_name' : $scope.virtualName,
                'volume_type': 'None',
                'is_root': false,
                'snapshot_id': $scope.newSnapshotID,
                'size': $scope.newSize,
                'delete_on_termination': $scope.newDOT
            };
            $scope.bdmTextarea.val(JSON.stringify(bdMapping));
            $scope.setInitialNewValues();  // Reset values
            $scope.initChosenSelector();
            newMappingEntry.focus();
        };
        $scope.removeDevice = function (key) {
            var bdMapping = $scope.bdMapping;
            delete bdMapping[key];
            $scope.bdmTextarea.val(JSON.stringify(bdMapping));
        };
        $scope.isEphemeral = function(val) {
            if (val.virtual_name && val.virtual_name.indexOf('ephemeral') == 0) return true;
            return false;
        };
        $scope.updateRootDeviceSize = function ($event, key, is_root) {
            var bdMappingText = $scope.bdmTextarea.val();
            if (bdMappingText && is_root) {
                var bdMapping = JSON.parse(bdMappingText);
                var rootDevice = bdMapping[key] || '';
                if (rootDevice) {
                    bdMapping[key]['size'] = parseInt($($event.target).val(), 10);
                    $scope.bdmTextarea.val(JSON.stringify(bdMapping));
                }
            }
        };
        $scope.updateRootDeviceDelete = function ($event, key, is_root) {
            var bdMappingText = $scope.bdmTextarea.val();
            if (bdMappingText && is_root) {
                var bdMapping = JSON.parse(bdMappingText);
                var rootDevice = bdMapping[key] || '';
                if (rootDevice) {
                    bdMapping[key]['delete_on_termination'] = ($($event.target).val().toLowerCase() === 'true');
                    $scope.bdmTextarea.val(JSON.stringify(bdMapping));
                }
            }
        };
        $scope.showDOTflag = function (mapping) {
            if (mapping.is_root) return true;
            if (mapping.volume_type !== 'ephemeral') return true;
            return false;
        };
    })
;
