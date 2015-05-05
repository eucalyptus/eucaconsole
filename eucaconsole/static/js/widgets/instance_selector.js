/**
 * @fileOverview Instance Selector Directive JS
 * @requires AngularJS
 *
 */

angular.module('EucaConsoleUtils').directive('instanceSelector', function() {
    return {
        restrict: 'E',
        scope: {
            option_json: '@options'
        },
        templateUrl: function (scope, elem) {
            return elem.template;
        },
        controller: function ($scope, $http, $timeout, eucaHandleError, eucaUnescapeJson) {
            $scope.allInstanceList = [];
            $scope.instanceList = [];
            $scope.selectedInstanceList = [];
            $scope.instancesJsonEndpoint = '';
            $scope.isVPCSupported = false;
            $scope.vpcNetwork = 'None';
            $scope.vpcSubnets = [];
            $scope.availabilityZones = [];
            $scope.searchQueryURL = '';
            $scope.searchFilter = '';
            $scope.filterKeys = [];
            $scope.tableText = {};
            $scope.initSelector = function () {
                var options = JSON.parse(eucaUnescapeJson($scope.option_json));
                $scope.setInitialValues(options);
                $scope.setWatcher();
                if ($scope.instancesJsonEndpoint !== '') {
                    $scope.getAllInstanceList();
                }
                // Workaround for the Bug in jQuery to prevent JS Uncaught TypeError
                // See http://stackoverflow.com/questions/27408501/ng-repeat-sorting-is-throwing-an-exception-in-jquery
                Object.getPrototypeOf(document.createComment('')).getAttribute = function() {};
            };
            $scope.setInitialValues = function (options) {
                $scope.allInstanceList = [];
                $scope.instanceList = [];
                $scope.selectedInstanceList = [];
                $scope.vpcNetwork = 'None';
                $scope.vpcSubnets = [];
                $scope.availabilityZones = [];
                $scope.isVPCSupported = false;
                $scope.searchQueryURL = '';
                $scope.searchFilter = '';
                $scope.filterKeys = [];
                if (options.hasOwnProperty('is_vpc_supported')) {
                    $scope.isVPCSupported = options.is_vpc_supported;
                }
                if (options.hasOwnProperty('instance_selector_text')) {
                    $scope.tableText = options.instance_selector_text;
                }
                if (options.hasOwnProperty('instances_json_endpoint')) {
                    $scope.instancesJsonEndpoint = options.instances_json_endpoint;
                }
                if (options.hasOwnProperty('all_instance_list')) {
                    $scope.allInstanceList = options.allInstance_list;
                }
            };
            $scope.setWatcher = function () {
                $scope.$watch('allInstanceList', function () {
                    $scope.updateInstanceList();
                }, true);
                $scope.$watch('selectedInstanceList', function () {
                    // Timeout is needed for the ng-repeat's table to update
                    $timeout(function() {
                        $scope.checkInstanceAllCheckbox();
                        $scope.matchInstanceCheckboxes();
                        if ($scope.vpcNetwork === 'None') { 
                            $scope.updateInstanceAvailabilityZones();
                        } else {
                            $scope.updateInstanceVPCSubnets();
                        }
                    });
                    $scope.$emit('eventUpdateSelectedInstanceList', $scope.selectedInstanceList);
                }, true);
                $scope.$watch('availabilityZones', function () {
                    $scope.$emit('eventUpdateAvailabilityZones', $scope.availabilityZones);
                }, true);
                $scope.$watch('vpcSubnets', function () {
                    $scope.$emit('eventUpdateVPCSubnets', $scope.vpcSubnets);
                }, true);
                $scope.$watch('vpcNetwork', function () {
                    $scope.updateInstanceList();
                });
                $scope.$on('eventQuerySearch', function ($event, query) {
                    $scope.searchQueryURL = '';
                    if (query.length > 0) {
                       $scope.searchQueryURL = query;
                    }
                    $scope.getAllInstanceList();
                });
                $scope.$on('eventTextSearch', function ($event, text, filterKeys) {
                    $scope.searchFilter = text;
                    $timeout(function () {
                        $scope.searchFilterItems(filterKeys);
                    });
                });
                $('#instance_selector').on('click', 'input:checkbox', function () {
                    var instanceID = $(this).val();
                    if (instanceID === '_all') {
                        // Clicked all checkbox
                        if ($(this).prop("checked") === true){
                            $scope.selectedInstanceList = [];
                            angular.forEach($scope.instanceList, function(instance) {
                                $scope.selectedInstanceList.push(instance);
                            });
                            $('#instance_selector input:checkbox').not(this).prop('checked', true);
                        } else {
                            $scope.selectedInstanceList = [];
                            $('#instance_selector input:checkbox').not(this).prop('checked', false);
                        }
                    } else {
                        // Click instance checkbox
                        $('#instance-all-checkbox').prop('checked', false);
                        if ($(this).prop("checked") === true){
                            var itemExists = false;
                            angular.forEach($scope.selectedInstanceList, function(instance, $index) {
                                if (instance.id === instanceID) {
                                    itemExists = true;
                                }
                            });
                            if (itemExists === false) {
                                angular.forEach($scope.instanceList, function(instance) {
                                    if (instance.id === instanceID) {
                                        $scope.selectedInstanceList.push(instance);
                                    }
                                });
                            }
                        } else {
                            angular.forEach($scope.selectedInstanceList, function(instance, $index) {
                                if (instance.id === instanceID) {
                                    $scope.selectedInstanceList.splice($index, 1);
                                } 
                            });
                        }
                    }
                    $scope.$apply();
                });
                $scope.$on('eventWizardUpdateAvailabilityZones', function ($event, availabilityZones) {
                    $scope.availabilityZones = availabilityZones;
                    $scope.updateSelectedInstanceListForAvailabilityZones();
                    $timeout(function() {
                        $scope.clearInstanceCheckboxes();
                        $scope.matchInstanceCheckboxes();
                    });
                });
                $scope.$on('eventWizardUpdateVPCSubnets', function ($event, vpcSubnets) {
                    $scope.vpcSubnets = vpcSubnets;
                    $scope.updateSelectedInstanceListForVPCSubnets();
                    $timeout(function() {
                        $scope.clearInstanceCheckboxes();
                        $scope.matchInstanceCheckboxes();
                    });
                });
                $scope.$on('eventWizardUpdateVPCNetwork', function ($event, vpcNetwork) {
                    $scope.vpcNetwork = vpcNetwork;
                });
                $scope.$on('eventInitSelectedInstances', function ($event, newSelectedInstances) {
                    $scope.initSelectedInstances(newSelectedInstances);
                });
            };
            $scope.getAllInstanceList = function () {
                var csrf_token = $('#csrf_token').val();
                var data = "csrf_token=" + csrf_token;
                if ($scope.searchQueryURL !== '') {
                    data = data + "&" + $scope.searchQueryURL;
                }
                $http({
                    method:'POST', url:$scope.instancesJsonEndpoint, data:data,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                }).success(function(oData) {
                    var results = oData ? oData.results : [];
                    $scope.allInstanceList = results;
                }).error(function (oData) {
                    eucaHandleError(oData, status);
                });
            };
            $scope.updateInstanceList = function () {
                var tempInstanceArray = [];
                angular.forEach($scope.allInstanceList, function (instance) {
                    if ($scope.vpcNetwork === 'None') {
                        if (instance.vpc_name === '') {
                            tempInstanceArray.push(instance);
                        }
                    } else {
                        if (instance.vpc_name !== '') {
                            tempInstanceArray.push(instance);
                        }
                    }
                });
                angular.copy(tempInstanceArray, $scope.instanceList);
                $scope.updateSelectedInstanceList();
                // Update the instance checkboxes to ensure the checked values are matched
                // timeout is needed for the table's display update to complete
                $timeout(function() {
                    $scope.matchInstanceCheckboxes();
                });
            };
            // Only keep the selected instances that are in the current instanceList
            $scope.updateSelectedInstanceList = function () {
                var dupList = $scope.selectedInstanceList.slice(0);
                $scope.selectedInstanceList = [];
                angular.forEach(dupList, function (selectedInstance, $index) {
                    angular.forEach($scope.instanceList, function (instance) {
                        if (selectedInstance.id === instance.id) {
                            $scope.selectedInstanceList.push(selectedInstance);
                        } 
                    });
                });
            };
            $scope.initSelectedInstances = function (newSelectedInstances) {
                var newList = [];
                angular.forEach(newSelectedInstances, function (instanceID) {
                    angular.forEach($scope.allInstanceList, function (instance) {
                        if (instance.id === instanceID) {
                            newList.push(instance);
                        } 
                    });
                });
                $scope.selectedInstanceList = newList;
            };
            $scope.updateSelectedInstanceListForAvailabilityZones = function () {
                var dupList = $scope.selectedInstanceList.slice(0);
                $scope.selectedInstanceList = [];
                angular.forEach(dupList, function (selectedInstance) {
                    angular.forEach($scope.instanceList, function (instance) {
                        if (selectedInstance.id === instance.id) {
                            var includesZone = false;
                            angular.forEach($scope.availabilityZones, function(zone) {
                                if (zone === instance.placement) {
                                    includesZone = true;
                                }
                            });
                            if (includesZone === true) {
                                $scope.selectedInstanceList.push(selectedInstance);
                            }
                        } 
                    });
                });
            };
            $scope.updateSelectedInstanceListForVPCSubnets = function () {
                var dupList = $scope.selectedInstanceList.slice(0);
                $scope.selectedInstanceList = [];
                angular.forEach(dupList, function (selectedInstance) {
                    angular.forEach($scope.instanceList, function (instance) {
                        if (selectedInstance.id === instance.id) {
                            var includesSubnet = false;
                            angular.forEach($scope.vpcSubnets, function(subnet) {
                                if (subnet === instance.subnet_id) {
                                    includesSubnet = true;
                                }
                            });
                            if (includesSubnet === true) {
                                $scope.selectedInstanceList.push(selectedInstance);
                            }
                        } 
                    });
                });
            };
            $scope.updateInstanceAvailabilityZones = function () {
                $scope.availabilityZones = [];
                angular.forEach($scope.selectedInstanceList, function (selectedInstance) {
                    angular.forEach($scope.instanceList, function (instance) {
                        if (selectedInstance.id === instance.id) {
                            var existsZone = false;
                            angular.forEach($scope.availabilityZones, function (zone) {
                                if (zone == instance.placement) {
                                    existsZone = true;
                                }
                            });
                            if (existsZone === false) {
                                $scope.availabilityZones.push(instance.placement);
                            }
                        } 
                    });
                });
            };
            $scope.updateInstanceVPCSubnets = function () {
                $scope.vpcSubnets = [];
                angular.forEach($scope.selectedInstanceList, function (selectedInstance) {
                    angular.forEach($scope.instanceList, function (instance) {
                        if (selectedInstance.id === instance.id) {
                            var existsSubnet = false;
                            angular.forEach($scope.vpcSubnets, function (subnet) {
                                if (subnet == instance.subnet_id) {
                                    existsSubnet = true;
                                }
                            });
                            if (existsSubnet === false) {
                                $scope.vpcSubnets.push(instance.subnet_id);
                            }
                        } 
                    });
                });
            };
            /*  Filter items client side based on search criteria.
             *  @param {array} filterProps Array of properties to filter items on
             */
            $scope.searchFilterItems = function(filterProps) {
                var filterText = ($scope.searchFilter || '').toLowerCase();
                if (filterProps !== '' && filterProps !== undefined){
                    // Store the filterProps input for later use as well
                    $scope.filterKeys = filterProps;
                }
                if (filterText === '') {
                    // If the search filter is empty, skip the filtering
                    $scope.instanceList = $scope.allInstanceList;
                    return;
                }
                // Leverage Array.prototype.filter (ECMAScript 5)
                var filteredItems = $scope.allInstanceList.filter(function(item) {
                    for (var i=0; i < $scope.filterKeys.length; i++) {  // Can't use $.each or Array.prototype.forEach here
                        var propName = $scope.filterKeys[i];
                        var itemProp = item.hasOwnProperty(propName) && item[propName];
                        if (itemProp && typeof itemProp === "string" && 
                            itemProp.toLowerCase().indexOf(filterText) !== -1) {
                                return item;
                        } else if (itemProp && typeof itemProp === "object") {
                            // In case of mutiple values, create a flat string and perform search
                            var flatString = $scope.getItemNamesInFlatString(itemProp);
                            if (flatString.toLowerCase().indexOf(filterText) !== -1) {
                                return item;
                            }
                        }
                    }
                });
                // Update the items[] with the filtered items
                $scope.instanceList = filteredItems;
            };
            $scope.checkInstanceAllCheckbox = function () {
                // When selectedInstanceList is empty and the select all checkbox is clicked, clear the checkbox
                if ($scope.selectedInstanceList.length === 0 && 
                    $('#instance-all-checkbox').prop('checked') === true) {
                    $('#instance-all-checkbox').prop('checked', false);
                }
            };
            $scope.clearInstanceCheckboxes = function () {
                angular.forEach($scope.allInstanceList, function(instance) {
                    var checkbox = $('#instance-checkbox-' + instance.id);
                    checkbox.prop("checked", false);
                });
            };
            $scope.matchInstanceCheckboxes = function () {
                // Ensure that the selectedInstanceList's items are checked when the table updates
                angular.forEach($scope.selectedInstanceList, function(instance) {
                    var checkbox = $('#instance-checkbox-' + instance.id);
                    if (checkbox.length > 0 && checkbox.prop("checked") === false){
                        checkbox.prop("checked", true);
                    }
                });
            };
            $scope.initSelector();
        }
    };
})
;
