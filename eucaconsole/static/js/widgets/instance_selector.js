/**
 * @fileOverview Instance Selector Directive JS
 * @requires AngularJS
 *
 */

eucaConsoleUtils.directive('instanceSelector', function() {
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
                $scope.instanceCount = 0;
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
		    $scope.$watch('allInstanceList', function(){
                       console.log($scope.allInstanceList); 
		    }, true);
		    $scope.$watch('instanceList', function(){
                       console.log($scope.instanceList); 
		    }, true);
                    $scope.$on('eventUpdateAvailabilityZones', function ($event, availabilityZones) {
                        console.log("availabilityZones: " + availabilityZones);
                    });
                    $scope.$on('eventUpdateVPCSubnets', function ($event, vpcSubnets) {
                        console.log("vpcSubnets: " + vpcSubnets);
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
                $scope.initSelector();
            }
        };
    })
;
