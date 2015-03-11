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
                        $scope.$emit('eventUpdateSelectedInstanceList', $scope.selectedInstanceList);
		    }, true);
                    $('#instance_selector').on('click', 'input:checkbox', function () {
                        var instanceID = $(this).val();
                        if (instanceID === '_all') {
                            // Clicked all checkbox
                            if ($(this).prop("checked") === true){
                                $scope.selectedInstanceList = [];
                                angular.forEach($scope.instanceList, function(instance) {
                                    $scope.selectedInstanceList.push(instance.id);
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
                                $scope.selectedInstanceList.push(instanceID);
                            } else {
                                angular.forEach($scope.selectedInstanceList, function(instance, $index) {
                                    if (instance === instanceID) {
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
                                if (instance.placement === zone) {
                                    $scope.instanceList.push(instance);
                                }
                            });
                        }
                    });
                };
                $scope.initSelector();
            }
        };
    })
;
