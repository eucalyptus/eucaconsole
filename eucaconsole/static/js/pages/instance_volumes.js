/**
 * @fileOverview Instance Volumes page JS
 * @requires AngularJS
 *
 */

angular.module('InstanceVolumes', ['EucaConsoleUtils'])
    .controller('InstanceVolumesCtrl', function ($scope, $http, $timeout, eucaUnescapeJson, eucaHandleError) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        // Volume states are: "attached", "attaching", "detaching"
        // 'detached' state doesn't apply here since it won't be attached to the instance
        $scope.loading = false;
        $scope.volumes = [];
        $scope.allVolumes = [];
        $scope.availableVolumes = {};
        $scope.availableVolumeCount = 0;
        $scope.instanceId = '';
        $scope.jsonEndpoint = '';
        $scope.initialLoading = true;
        $scope.detachFormAction = '';
        $scope.isDialogHelpExpanded = false;
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.instanceId = options['instance_id'];
            $scope.jsonEndpoint = options['instance_volumes_json_url'];
            $scope.initChosenSelector();
            $scope.getInstanceVolumes();
            $scope.setWatch();
            $scope.setFocus();
            $scope.setDropdownMenusListener();
        };
        $scope.initChosenSelector = function () {
            $(document).ready(function() {
                $('#attach-volume-modal').on('open', function() {
                    $('#volume_id').chosen({'width': '100%', search_contains: true});
                });
            });
        };
        $scope.setWatch = function () {
            $scope.$watch('availableVolumes', function() {
                // Timeout is needed to ensure angular update is complete
                $timeout(function() { 
                    $('#volume_id').trigger('chosen:updated');
                });
            }, true); 
        }
        $scope.setFocus = function () {
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var inputElement = modal.find('input[type!=hidden]').get(0);
                var modalButton = modal.find('button').get(0);
                if (!!inputElement) {
                    inputElement.focus();
                } else if (!!modalButton) {
                    modalButton.focus();
                }
            });
        };
        $scope.setDropdownMenusListener = function () {
            var modals = $('[data-reveal]');
            modals.on('open', function () {
                $('.gridwrapper').find('.f-dropdown').filter('.open').css('display', 'none');
            });
            modals.on('close', function () {
                $('.gridwrapper').find('.f-dropdown').filter('.open').css('display', 'block');
            })
        };
        $scope.getInstanceVolumes = function () {
            $http.get($scope.jsonEndpoint).success(function(oData) {
                var transitionalCount = 0;
                $scope.volumes = [];
                $scope.availableVolumes = {};
                $scope.availableVolumeCount = 0;
                $scope.allVolumes = oData ? oData.results : [];
                $scope.initialLoading = false;
                // Detect if any volume states are transitional
                $scope.allVolumes.forEach(function(volume) {
                    if (volume['attach_instance_id'] == $scope.instanceId) {
                        $scope.volumes.push(volume);
                    } else if (volume['status'] == 'available') {
                        $scope.availableVolumes[volume['id']] = volume['name'];
                        $scope.availableVolumeCount += 1;
                    }
                    if (volume['transitional']) {
                        transitionalCount += 1;
                    }
                });
                // Auto-refresh volumes if any of them are transitional
                if (transitionalCount > 0) {
                    $timeout(function() {$scope.getInstanceVolumes()}, 4000);  // Poll every 4 seconds
                }
            }).error(function (oData, status) {
                eucaHandleError(oData, status);
            });
        };
        $scope.revealDetachModal = function (action, name) {
            var modal = $('#detach-volume-modal');
            $scope.detachFormAction = action;
            modal.foundation('reveal', 'open');
        };
        $scope.detachModal = function (volume, device_name, url, action) {
            $scope.detachVolumeName = volume;
            $scope.detachFormAction = action;
            $http.get(url).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    if (results.root_device_name == device_name) {
                        $('#detach-volume-warn-modal').foundation('reveal', 'open');
                    } else {
                        $('#detach-volume-modal').foundation('reveal', 'open');
                    }
                }
            });
        };
    })
;

