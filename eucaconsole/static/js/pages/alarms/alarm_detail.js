angular.module('AlarmDetailPage', [
    'AlarmsComponents', 'EucaChosenModule', 'ChartAPIModule', 'ChartServiceModule',
    'AlarmServiceModule'
])
.directive('alarmDetail', function () {
    return {
        restrict: 'A',
        link: function (scope, element, attrs) {
            scope.alarm = JSON.parse(attrs.alarmDetail);

            var dimensions = [];
            Object.keys(scope.alarm.dimensions).forEach(function (key) {
                var val = scope.alarm.dimensions[key],
                    result;
                val.forEach(function (current) {
                    result = {};
                    result[key] = [current];
                    dimensions.push(JSON.stringify(result));
                });
            });
            scope.alarm.dimensions = dimensions;
        },
        controller: ['$scope', '$window', 'AlarmService', function ($scope, $window, AlarmService) {
            var csrf_token = $('#csrf_token').val();

            $scope.saveChanges = function (event) {
                var servicePath = event.target.dataset.servicePath;

                AlarmService.updateAlarm($scope.alarm, servicePath, csrf_token, true)
                    .then(function success (response) {
                        $window.location.href = servicePath;
                    }, function error (response) {
                        $window.location.href = servicePath;
                    });
            };

            $scope.delete = function (event) {
                event.preventDefault();
                var redirectPath = event.target.dataset.redirectPath;
                var servicePath = event.target.dataset.servicePath;

                var alarms = [{
                    name: $scope.alarm.name
                }];

                AlarmService.deleteAlarms(alarms, servicePath, csrf_token, true)
                    .then(function success (response) {
                        $window.location.href = redirectPath;
                    }, function error (response) {
                        Notify.failure(response.data.message);
                    }); 
            };

        }]
    };
})
.directive('metricChart', function () {
    return {
        restrict: 'A',
        scope: {
            metric: '@',
            namespace: '@',
            duration: '=',
            statistic: '=',
            unit: '@',
            dimensions: '='
        },
        link: function (scope, element) {
            scope.target = element[0];
        },
        controller: ['$scope', 'CloudwatchAPI', 'ChartService',
        function ($scope, CloudwatchAPI, ChartService) {

            // ids and idtype comes from passed in dimensions
            // iterate over dimensions, will need a separate
            // chart line for each dimension
            //
            $scope.$watch('dimensions', function (x) {
                if(!x) {
                    return;
                }

                Object.keys($scope.dimensions).forEach(function (dimension) {
                    var ids = $scope.dimensions[dimension];

                    CloudwatchAPI.getChartData({
                        ids: ids,
                        idtype: dimension,
                        metric: $scope.metric,
                        namespace: $scope.namespace,
                        duration: $scope.duration,
                        statistic: $scope.statistic,
                        unit: $scope.unit
                    }).then(function(oData) {
                        var results = oData ? oData.results : '';
                        var chart = ChartService.renderChart($scope.target, results, {
                            unit: oData.unit || scope.unit
                        });
                    });
                });
            });

        }]
    };
})
.directive('alarmActions', function () {
    return {
        restrict: 'A',
        link: function (scope, element, attrs) {
            scope.alarmActions = JSON.parse(attrs.alarmActions);
            scope.servicePath = attrs.servicePath;
        },
        controller: ['$scope', 'AlarmService', 'ScalingGroupsService', function ($scope, AlarmService, ScalingGroupsService) {
            $scope.addAction = function () {
                //  Do not add action if form is invalid
                if($scope.alarmActionsForm.$invalid) {
                    return;
                }

                var policyName = $scope.action.scalingGroupPolicy,
                    policy = $scope.scalingGroupPolicies[policyName];

                //  Do not add action if duplicate
                var duplicate = $scope.alarmActions.some(function (current) {
                    return current.arn == policy.arn;
                });
                if(duplicate) {
                    return;
                }

                var action = {
                    autoscaling_group_name: $scope.action.scalingGroup,
                    policy_name: policyName,
                    arn: policy.arn,
                    scaling_adjustment: policy.scaling_adjustment
                };
                $scope.alarmActions.push(action);

                $scope.updateActions();
            };

            $scope.removeAction = function ($index) {
                $scope.alarmActions.splice($index, 1);
                $scope.updateActions();
            };

            $scope.updateActions = function () {
                AlarmService.updateActions($scope.alarmActions, $scope.servicePath).then(function success () {
                    $scope.resetForm();
                }, function error (response) {
                    console.log(response);
                });
            };

            $scope.resetForm = function () {
                $scope.action = {
                    alarmState: 'ALARM'
                };
                $scope.scalingGroupPolicies = [];
                $scope.alarmActionsForm.$setPristine();
                $scope.alarmActionsForm.$setUntouched();
            };

            $scope.policiesAvailable = function () {
                var policies = $scope.scalingGroupPolicies || {};
                return !Object.keys(policies).length;
            };

            $scope.updatePolicies = function () {
                ScalingGroupsService.getPolicies($scope.action.scalingGroup)
                    .then(function success (data) {
                        var policies = data.policies,
                            filtered = {};

                        var availableKeys = Object.keys(policies).filter(function (key) {
                            return !$scope.alarmActions.some(function (action) {
                                return action.policy_name == key;
                            });
                        });

                        $scope.scalingGroupPolicies = {};
                        availableKeys.forEach(function (key) {
                            $scope.scalingGroupPolicies[key] = policies[key];
                        });
                    }, function error (response) {
                        console.log(response);
                    });
            };
        }]
    };
})
.factory('ScalingGroupsService', ['$http', '$interpolate', function ($http, $interpolate) {
    var getPolicyUrl = $interpolate('/scalinggroups/{{ id }}/policies/json');
    return {
        getPolicies: function (id) {
            var policyUrl = getPolicyUrl({id: id});
            return $http({
                method: 'GET',
                url: policyUrl
            }).then(function success (response) {
                var data = response.data || {
                    policies: {}
                };
                return data;
            }, function error (response) {
                return response;
            });
        }
    };
}])
.filter('signed', function () {
    return function (input) {
        input = Number(input);
        if(input > 0) {
            return '+' + input.toString(10);
        }
        return input.toString(10);
    };
});
