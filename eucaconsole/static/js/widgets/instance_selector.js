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
                $scope.vpcSubnets = [];
                $scope.availabilityZones = [];
                $scope.searchQueryURL = '';
                $scope.searchFilter = '';
                $scope.filterKeys = [];
		$scope.initSelector = function () {
		    var options = JSON.parse(eucaUnescapeJson($scope.option_json));
		    $scope.setInitialValues(options);
		    $scope.setWatcher();
		    $scope.setFocus();
                    if ($scope.instancesJsonEndpoint !== '') {
                        $scope.getAllInstanceList();
                    }
		};
                $scope.setInitialValues = function (options) {
                    $scope.allInstanceList = [];
                    $scope.instanceList = [];
                    $scope.selectedInstanceList = [];
                    $scope.vpcSubnets = [];
                    $scope.availabilityZones = [];
                    $scope.isVPCSupported = false;
                    $scope.searchQueryURL = '';
                    $scope.searchFilter = '';
                    $scope.filterKeys = [];
                    if (options.hasOwnProperty('is_vpc_supported')) {
                        $scope.isVPCSupported = options.is_vpc_supported;
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
                        // When selectedInstanceList is empty and the select all checkbox is clicked, clear the checkbox
                        if ($scope.selectedInstanceList.length === 0 && 
                            $('#instance-all-checkbox').prop('checked') === true) {
                            $('#instance-all-checkbox').prop('checked', false);
                        }
                        $scope.$emit('eventUpdateSelectedInstanceList', $scope.selectedInstanceList);
		    }, true);
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
                        var instanceName = $('#instance-name-' + instanceID).text();
                        if (instanceID === '_all') {
                            // Clicked all checkbox
                            if ($(this).prop("checked") === true){
                                $scope.selectedInstanceList = [];
                                angular.forEach($scope.instanceList, function(instance) {
                                    $scope.selectedInstanceList.push(instance.name);
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
                                    if (instance === instanceID || instance === instanceName) {
                                        itemExists = true;
                                    }
                                });
                                if (itemExists === false) {
                                    $scope.selectedInstanceList.push(instanceName);
                                }
                            } else {
                                angular.forEach($scope.selectedInstanceList, function(instance, $index) {
                                    if (instance === instanceID || instance === instanceName) {
                                        $scope.selectedInstanceList.splice($index, 1);
                                    } 
                                });
                            }
                        }
                        $scope.$apply();
                    });
                    $scope.$on('eventUpdateAvailabilityZones', function ($event, availabilityZones) {
                        $scope.vpcSubnets = [];
                        $scope.availabilityZones = availabilityZones;
                        $scope.updateInstanceList();
                    });
                    $scope.$on('eventUpdateVPCSubnets', function ($event, vpcSubnets) {
                        $scope.availabilityZones = [];
                        $scope.vpcSubnets = vpcSubnets;
                        $scope.updateInstanceList();
                    });
		};
		$scope.setFocus = function () {
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
                    $scope.instanceList = [];
                    angular.forEach($scope.allInstanceList, function (instance) {
                        if ($scope.vpcSubnets.length > 0) {
                            angular.forEach($scope.vpcSubnets, function (vpcSubnet) {
                                if (instance.subnet_id === vpcSubnet) {
                                    $scope.instanceList.push(instance);
                                }
                            });
                        } else if ($scope.availabilityZones.length > 0) {
                            angular.forEach($scope.availabilityZones, function (zone) {
                                if (instance.placement === zone && instance.subnet_id === null) {
                                    $scope.instanceList.push(instance);
                                }
                            });
                        }
                    });
                    $scope.updateSelectedInstanceList();
                };
                // Only keep the selected instances that are in the current instanceList
                $scope.updateSelectedInstanceList = function () {
                    var dupList = $scope.selectedInstanceList.slice(0);
                    $scope.selectedInstanceList = [];
                    angular.forEach(dupList, function (selectedInstance, $index) {
                        angular.forEach($scope.instanceList, function (instance) {
                            if (selectedInstance.indexOf(instance.id) > -1) {
                                $scope.selectedInstanceList.push(selectedInstance);
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
                $scope.initSelector();
            }
        };
    })
;
