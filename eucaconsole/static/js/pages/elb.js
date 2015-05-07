/**
 * @fileOverview ELB Detail Page JS
 * @requires AngularJS
 *
 */

angular.module('ELBPage', ['EucaConsoleUtils', 'ELBListenerEditor', 'TagEditor', 'MagicSearch'])
    .controller('ELBPageCtrl', function ($scope, $timeout, eucaUnescapeJson) {
        $scope.isNotChanged = true;
        $scope.securityGroups = [];
        $scope.availabilityZones = []; 
        $scope.selectedZoneList = [];
        $scope.allZoneList = [];
        $scope.vpcNetwork = 'None';
        $scope.vpcSubnetList = [];
        $scope.selectedVPCSubnetList = [];
        $scope.allVPCSubnetList = [];
        $scope.allInstanceList = [];
        $scope.ELBInstanceHealthList = [];
        $scope.instanceList = [];
        $scope.pingProtocol = '';
        $scope.pingPort = '';
        $scope.pingPath = '';
        $scope.responseTimeout = '';
        $scope.timeBetweenPings = '';
        $scope.failuresUntilUnhealthy = '';
        $scope.passesUntilHealthy = '';
        $scope.unsavedChangesWarningModalLeaveCallback = null;
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.setInitialValues(options);
            $scope.setWatch();
            $scope.setFocus();
        };
        $scope.setInitialValues = function (options) {
            if (options.hasOwnProperty('securitygroups')) {
                if (options.securitygroups instanceof Array && options.securitygroups.length > 0) {
                    $scope.securityGroups = options.securitygroups;
                    // Timeout is needed for chosen to react after Angular updates the options
                    $timeout(function(){
                        $('#securitygroup').trigger('chosen:updated');
                    }, 500);
                }
            }
            if (options.hasOwnProperty('in_use')) {
                $scope.elbInUse = options.in_use;
            }
            if (options.hasOwnProperty('has_image')) {
                $scope.hasImage = options.has_image;
            }
            if (!$scope.hasImage) {
                $('#image-missing-modal').foundation('reveal', 'open');
            }
            if (options.hasOwnProperty('availability_zone_choices')) {
                $scope.allZoneList = options.availability_zone_choices;
            }
            if (options.hasOwnProperty('availability_zones')) {
                $scope.availabilityZones = options.availability_zones;
                // Timeout is needed for the instance selector to be initizalized
                $timeout(function () {
                    $scope.$broadcast('eventUpdateAvailabilityZones', $scope.availabilityZones);
                }, 500);
            }
            if (options.hasOwnProperty('vpc_subnet_choices')) {
                $scope.allVPCSubnetList = options.vpc_subnet_choices;
            }
            if (options.hasOwnProperty('elb_vpc_network')) {
                if (options.elb_vpc_network !== null) {
                    $scope.vpcNetwork = options.elb_vpc_network;
                    // Timeout is needed for the instance selector to be initizalized
                    $timeout(function () {
                        $scope.$broadcast('eventWizardUpdateVPCNetwork', $scope.vpcNetwork);
                    }, 500);
                }
            }
            if (options.hasOwnProperty('elb_vpc_subnets')) {
                $scope.vpcSubnetList = options.elb_vpc_subnets;
            }
            if (options.hasOwnProperty('all_instances')) {
                $scope.allInstanceList = options.all_instances;
            }
            if (options.hasOwnProperty('elb_instance_health')) {
                $scope.ELBInstanceHealthList = options.elb_instance_health;
            }
            if (options.hasOwnProperty('instances')) {
                $scope.instanceList = options.instances;
                // Timeout is needed for the instance selector to be initizalized
                $timeout(function () {
                    $scope.$broadcast('eventInitSelectedInstances', $scope.instanceList);
                }, 2000);
            }
            if (options.hasOwnProperty('health_check_ping_protocol')) {
                $scope.pingProtocol = options.health_check_ping_protocol;
            }
            if (options.hasOwnProperty('health_check_ping_port')) {
                $scope.pingPort = parseInt(options.health_check_ping_port);
            }
            if (options.hasOwnProperty('health_check_ping_path')) {
                $scope.pingPath = options.health_check_ping_path;
            }
            if (options.hasOwnProperty('health_check_interval')) {
                $scope.timeBetweenPings = options.health_check_interval;
            }
            if (options.hasOwnProperty('health_check_timeout')) {
                $scope.responseTimeout = options.health_check_timeout;
            }
            if (options.hasOwnProperty('health_check_unhealthy_threshold')) {
                $scope.failuresUntilUnhealthy = options.health_check_unhealthy_threshold;
            }
            if (options.hasOwnProperty('health_check_healthy_threshold')) {
                $scope.passesUntilHealthy = options.health_check_healthy_threshold;
            }
            $scope.initChosenSelectors(); 
        };
        $scope.initChosenSelectors = function () {
            $('#securitygroup').chosen({'width': '100%', search_contains: true});
        };
        $scope.setWatch = function () {
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');
                $(this).find('.dialog-progress-display').css('display', 'block');
            });
            $scope.$watch('availabilityZones', function () {
                $scope.updateSelectedZoneList();
                $scope.$broadcast('eventUpdateAvailabilityZones', $scope.availabilityZones);
            }, true);
            $scope.$watch('vpcSubnetList', function () {
                $scope.updateSelectedVPCSubnetList();
            }, true);
            $scope.$watch('instanceList', function () {
                $scope.$broadcast('eventInitSelectedInstances', $scope.instanceList);
            }, true);
            $scope.$on('searchUpdated', function ($event, query) {
                // Relay the query search update signal
                $scope.$broadcast('eventQuerySearch', query);
            });
            $scope.$on('textSearch', function ($event, searchVal, filterKeys) {
                // Relay the text search update signal
                $scope.$broadcast('eventTextSearch', searchVal, filterKeys);
            });
        };
        $scope.setFocus = function () {
            $(document).on('ready', function(){
                $('.actions-menu').find('a').get(0).focus();
            });
            $(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
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
        $scope.clickTab = function ($event, tab){
            $event.preventDefault();
            // If there exists unsaved changes, open the warning modal instead
            if ($scope.isNotChanged === false) {
                // $scope.openModalById('unsaved-changes-warning-modal');
                $scope.unsavedChangesWarningModalLeaveCallback = function() {
                    $scope.isNotChanged = true;
                    $scope.toggleTab(tab);
                    // $('#unsaved-changes-warning-modal').foundation('reveal', 'close');
                };
                return;
            } 
            $scope.toggleTab(tab);
        };
        $scope.toggleTab = function (tab) {
            $(".tabs").children("dd").each(function() {
                var id = $(this).find("a").attr("href").substring(1);
                var $container = $("#" + id);
                $(this).removeClass("active");
                $container.removeClass("active");
                if (id == tab || $container.find("#" + tab).length) {
                    $(this).addClass("active");
                    $container.addClass("active");
                    $scope.currentTab = id; // Update the currentTab value for the help display
                    $scope.$broadcast('updatedTab', $scope.currentTab);
                }
            });
        };
        $scope.updateSelectedZoneList = function () {
            var selected = [];
            angular.forEach($scope.availabilityZones, function (zoneID) {
                angular.forEach($scope.allZoneList, function (zone) {
                    if (zoneID === zone.id) {
                        zone.instanceCount = $scope.getInstanceCountInZone(zone);
                        zone.unhealthyInstanceCount = $scope.getUnhealthyInstanceCountInZone(zone);
                        selected.push(zone);
                        
                    }
                });
            });
            $scope.selectedZoneList = selected;
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
        $scope.submitSaveChanges = function ($event) {
        };
    })
;
