/**
 * @fileOverview ELB Instances Page JS
 * @requires AngularJS
 *
 */

angular.module('ELBInstancesPage', ['EucaConsoleUtils', 'MagicSearch'])
    .controller('ELBInstancesPageCtrl', function ($scope, $timeout, eucaUnescapeJson, eucaHandleUnsavedChanges) {
        $scope.availabilityZones = [];
        $scope.selectedZoneList = [];
        $scope.unselectedZoneList = [];
        $scope.allZoneList = [];
        $scope.vpcNetwork = 'None';
        $scope.newVPCSubnet = 'None';
        $scope.newZone = 'None';
        $scope.vpcSubnetList = [];
        $scope.selectedVPCSubnetList = [];
        $scope.unselectedVPCSubnetList = [];
        $scope.allVPCSubnetList = [];
        $scope.allInstanceList = [];
        $scope.ELBInstanceHealthList = [];
        $scope.instanceList = [];
        $scope.isNotChanged = true;
        $scope.isNotValid = false;
        $scope.isInitComplete = false;
        $scope.isCrossZoneEnabled = false;
        $scope.instanceCounts = {};
        $scope.unsavedChangesWarningModalLeaveCallback = null;
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.setInitialValues(options);
            $scope.setWatch();
            $timeout(function(){
                $scope.isInitComplete = true;
            }, 1000);
        };
        $scope.setInitialValues = function (options) {
            $scope.allZoneList = options.availability_zone_choices;
            $scope.availabilityZones = options.availability_zones;
            $scope.isCrossZoneEnabled = options.cross_zone_enabled;
            // Timeout is needed for the instance selector to be initizalized
            $timeout(function () {
                $scope.$broadcast('eventUpdateAvailabilityZones', $scope.availabilityZones);
            }, 500);
            $scope.allVPCSubnetList = options.vpc_subnet_choices;
            if (options.elb_vpc_network !== null) {
                $scope.vpcNetwork = options.elb_vpc_network;
                // Timeout is needed for the instance selector to be initizalized
                $timeout(function () {
                    $scope.$broadcast('eventWizardUpdateVPCNetwork', $scope.vpcNetwork);
                }, 500);
            }
            $scope.vpcSubnetList = options.elb_vpc_subnets;
            $scope.allInstanceList = options.all_instances;
            $scope.ELBInstanceHealthList = options.elb_instance_health;
            $scope.instanceList = options.instances;
            // Timeout is needed for the instance selector to be initizalized
            $timeout(function () {
                $scope.$broadcast('eventInitSelectedInstances', $scope.instanceList);
            }, 2000);
        };
        $scope.setWatch = function () {
            eucaHandleUnsavedChanges($scope);
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');
                $(this).find('.dialog-progress-display').css('display', 'block');
            });
            $scope.$watch('availabilityZones', function () {
                $scope.updateSelectedZoneList();
                $scope.$broadcast('eventUpdateAvailabilityZones', $scope.availabilityZones);
            }, true);
            $scope.$watch('selectedZoneList', function (newVal) {
                $scope.updateUnselectedZoneList();
                if ($scope.isInitComplete === true) {
                    $scope.isNotChanged = false;
                }
                if ($scope.vpcNetwork === 'None') {
                    $scope.isNotValid = newVal.length === 0;
                }
            }, true);
            $scope.$watch('vpcSubnetList', function () {
                $scope.updateSelectedVPCSubnetList();
            }, true);
            $scope.$watch('selectedVPCSubnetList', function (newVal) {
                $scope.updateUnselectedVPCSubnetList();
                if ($scope.isInitComplete === true) {
                    $scope.isNotChanged = false;
                }
                if ($scope.vpcNetwork !== 'None') {
                    $scope.isNotValid = newVal.length === 0;
                }
            }, true);
            $scope.$watch('instanceList', function () {
                $scope.$broadcast('eventInitSelectedInstances', $scope.instanceList);
            }, true);
            $scope.$watch('isCrossZoneEnabled', function () {
                if ($scope.isInitComplete === true) {
                    $scope.isNotChanged = false;
                }
            });
            $scope.$on('searchUpdated', function ($event, query) {
                // Relay the query search update signal
                $scope.$broadcast('eventQuerySearch', query);
            });
            $scope.$on('textSearch', function ($event, searchVal, filterKeys) {
                // Relay the text search update signal
                $scope.$broadcast('eventTextSearch', searchVal, filterKeys);
            });
            $scope.$on('eventUpdateListenerArray', function ($event, listenerArray) {
                if ($scope.isInitComplete === true) {
                    $scope.isNotChanged = false;
                }
                $scope.listenerArray = listenerArray;
            });
            $(document).on('click', '#instances-tab input[type="checkbox"]', function () {
                $scope.isNotChanged = false;
                $scope.$apply();
            });
            // Leave button is clicked on the warning unsaved changes modal
            $(document).on('click', '#unsaved-changes-warning-modal-stay-button', function () {
                $('#unsaved-changes-warning-modal').foundation('reveal', 'close');
            });
            // Stay button is clicked on the warning unsaved changes modal
            $(document).on('click', '#unsaved-changes-warning-modal-leave-link', function () {
                $scope.unsavedChangesWarningModalLeaveCallback();
            });
        };
        $scope.openModalById = function (modalID) {
            var modal = $('#' + modalID);
            modal.foundation('reveal', 'open');
            modal.find('h3').click();  // Workaround for dropdown menu not closing
        };
        $scope.updateSelectedZoneList = function () {
            var selected = [];
            angular.forEach($scope.availabilityZones, function (zoneID) {
                angular.forEach($scope.allZoneList, function (zone) {
                    zone.instanceCount = $scope.getInstanceCountInZone(zone);
                    zone.unhealthyInstanceCount = $scope.getUnhealthyInstanceCountInZone(zone);
                    if (zoneID === zone.id) {
                        selected.push(zone);
                    }
                });
            });
            $scope.selectedZoneList = selected;
        };
        $scope.updateUnselectedZoneList = function () {
            var allList = $scope.allZoneList;
            var unselected = [];
            var placeholder = {};
            placeholder.id = 'None';
            placeholder.name = $('#hidden_zone_selector_placeholder').text();
            unselected.push(placeholder);
            angular.forEach(allList, function (zone) {
                var isSelected = false;
                angular.forEach($scope.selectedZoneList, function (thisZone, $index) {
                    if (thisZone.id === zone.id) {
                       isSelected = true;
                    }
                });
                if (isSelected === false) {
                    zone.instanceCount = $scope.getInstanceCountInZone(zone);
                    zone.unhealthyInstanceCount = $scope.getUnhealthyInstanceCountInZone(zone);
                    unselected.push(zone);
                }
            });
            $scope.unselectedZoneList = unselected;
            $scope.newZone = placeholder;
        };
        $scope.updateSelectedVPCSubnetList = function () {
            var selected = [];
            angular.forEach($scope.vpcSubnetList, function (subnetID) {
                angular.forEach($scope.allVPCSubnetList, function (subnet) {
                    if (subnetID === subnet.id) {
                        subnet.instanceCount = $scope.getInstanceCountInSubnet(subnet.id);
                        subnet.unhealthyInstanceCount = $scope.getUnhealthyInstanceCountInSubnet(subnet.id);
                        selected.push(subnet);
                    }
                });
            });
            $scope.selectedVPCSubnetList = selected;
        };
        $scope.updateUnselectedVPCSubnetList = function () {
            var allList = $scope.allVPCSubnetList;
            var unselected = [];
            var placeholder = {};
            placeholder.id = 'None';
            placeholder.name = $('#hidden_subnet_selector_placeholder').text();
            unselected.push(placeholder);
            angular.forEach(allList, function (subnet) {
                var isSelected = false;
                angular.forEach($scope.selectedVPCSubnetList, function (thisSubnet, $index) {
                    if (thisSubnet.id === subnet.id) {
                       isSelected = true;
                    }
                });
                if (isSelected === false && subnet.vpc_id === $scope.vpcNetwork) {
                    subnet.instanceCount = $scope.getInstanceCountInSubnet(subnet.id);
                    subnet.unhealthyInstanceCount = $scope.getUnhealthyInstanceCountInSubnet(subnet.id);
                    unselected.push(subnet);
                }
            });
            $scope.unselectedVPCSubnetList = unselected;
            $scope.newVPCSubnet = placeholder;
        };
        $scope.getInstanceCountInZone = function (zone) {
            var count = 0;
            angular.forEach($scope.ELBInstanceHealthList, function (instanceHealth) {
                angular.forEach($scope.allInstanceList, function (instance) {
                    if (instanceHealth.instance_id === instance.id) {
                        if (instance.zone === zone.id) {
                            count += 1;
                        }
                    }
                });
            });
            return count;
        };
        $scope.getInstanceCountInSubnet = function (subnetID) {
            var count = 0;
            angular.forEach($scope.ELBInstanceHealthList, function (instanceHealth) {
                angular.forEach($scope.allInstanceList, function (instance) {
                    if (instanceHealth.instance_id === instance.id) {
                        if (instance.subnet_id === subnetID) {
                            count += 1;
                        }
                    }
                });
            });
            return count;
        };
        $scope.getUnhealthyInstanceCountInZone = function (zone) {
            var count = 0;
            angular.forEach($scope.ELBInstanceHealthList, function (instanceHealth) {
                if (instanceHealth.state === 'OutOfService') {
                    angular.forEach($scope.allInstanceList, function (instance) {
                        if (instanceHealth.instance_id === instance.id) {
                            if (instance.zone === zone.id) {
                                count += 1;
                            }
                        }
                    });
                }
            });
            return count;
        };
        $scope.getUnhealthyInstanceCountInSubnet = function (subnetID) {
            var count = 0;
            angular.forEach($scope.ELBInstanceHealthList, function (instanceHealth) {
                if (instanceHealth.state === 'OutOfService') {
                    angular.forEach($scope.allInstanceList, function (instance) {
                        if (instanceHealth.instance_id === instance.id) {
                            if (instance.subnet_id === subnetID) {
                                count += 1;
                            }
                        }
                    });
                }
            });
            return count;
        };
        $scope.clickEnableZone = function ($event) {
            $event.preventDefault();
            if ($scope.newZone.id === 'None') {
                return;
            }
            angular.forEach($scope.unselectedZoneList, function (zone, $index) {
                if ($scope.newZone.id === zone.id) {
                    $scope.selectedZoneList.push(zone);
                    $scope.unselectedZoneList.splice($index, 1);
                }
            });
        };
        $scope.clickEnableVPCSubnet = function ($event) {
            $event.preventDefault();
            if ($scope.newVPCSubnet.id === 'None') {
                return;
            }
            angular.forEach($scope.unselectedVPCSubnetList, function (subnet, $index) {
                if ($scope.newVPCSubnet.id === subnet.id) {
                    $scope.selectedVPCSubnetList.push(subnet);
                    $scope.unselectedVPCSubnetList.splice($index, 1);
                }
            });
        };
        $scope.clickDisableZone = function (thisZoneID) {
            angular.forEach($scope.selectedZoneList, function (zone, $index) {
                if (thisZoneID === zone.id) {
                    $scope.selectedZoneList.splice($index, 1);
                    $scope.unselectedZoneList.push(zone);
                }
            });
        };
        $scope.clickDisableVPCSubnet = function (thisSubnetID) {
            angular.forEach($scope.selectedVPCSubnetList, function (subnet, $index) {
                if (thisSubnetID === subnet.id) {
                    $scope.selectedVPCSubnetList.splice($index, 1);
                    $scope.unselectedVPCSubnetList.push(subnet);
                }
            });
        };
    })
;
