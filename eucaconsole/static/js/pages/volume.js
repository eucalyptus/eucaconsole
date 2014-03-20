/**
 * @fileOverview Volume page JS
 * @requires AngularJS
 *
 */

// Volume page includes the tag editor, so pull in that module as well.
angular.module('VolumePage', ['TagEditor'])
    .controller('VolumePageCtrl', function ($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.volumeStatusEndpoint = '';
        $scope.transitionalStates = ['creating', 'deleting', 'attaching', 'detaching'];
        $scope.volumeStatus = '';
        $scope.volumeAttachStatus = '';
        $scope.snapshotId = '';
        $scope.instanceId = '';
        $scope.isUpdating = false;
        $scope.fromSnapshot = false;
        $scope.isTransitional = function (state) {
            return $scope.transitionalStates.indexOf(state) !== -1;
        };
        $scope.populateVolumeSize = function () {
            $http.get("/snapshots/"+$scope.snapshotId+"/size/json").success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $('input#size').val(results);
                }
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
                if (errorMsg && status === 403) {
                    alert(errorMsg);
                    $('#euca-logout-form').submit();
                }
            });
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
            snapshotField.chosen({'width': '75%', 'search_contains': true});
            // Instance choices in "Attach to instance" modal dialog
            $('#attach-volume-modal').on('open', function() {
                $('#instance_id').chosen({'width': '75%', search_contains: true});
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
            $scope.setFocus();
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
        $scope.getDeviceSuggestion = function () {
            $http.get("/instances/"+$scope.instanceId+"/nextdevice/json").success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $('input#device').val(results);
                }
            });
        };
        $scope.setFocus = function () {
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var modalID = $(this).attr('id');
                if( modalID.match(/terminate/)  || modalID.match(/delete/) || modalID.match(/release/) ){
                    var closeMark = modal.find('.close-reveal-modal');
                    if(!!closeMark){
                        closeMark.focus();
                    }
                }else{
                    var inputElement = modal.find('input[type!=hidden]').get(0);
                    var modalButton = modal.find('button').get(0);
                    if (!!inputElement) {
                        inputElement.focus();
                    } else if (!!modalButton) {
                        modalButton.focus();
                    }
               }
            });
        };
    })
;

