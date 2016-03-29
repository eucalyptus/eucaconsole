angular.module('AlarmActionsModule', ['AlarmServiceModule', 'ScalingGroupsServiceModule'])
.directive('alarmActions', function () {
    return {
        restrict: 'A',
        link: function (scope, element, attrs) {
            scope.alarmActions = JSON.parse(attrs.alarmActions);
            scope.servicePath = attrs.servicePath;
            scope.defaultOptionValue = 'Select policy...';
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
                $scope.defaultOptionValue = 'Select policy...';
                $scope.scalingGroupPolicies = [];
                $scope.alarmActionsForm.$setPristine();
                $scope.alarmActionsForm.$setUntouched();
            };

            $scope.policiesAvailable = function () {
                var policies = $scope.scalingGroupPolicies || {};
                return !Object.keys(policies).length;
            };

            $scope.updatePolicies = function () {
                if($scope.action.scalingGroup === '') {
                    $scope.resetForm();
                    return;
                }

                ScalingGroupsService.getPolicies($scope.action.scalingGroup)
                    .then(function success (data) {
                        var policies = data.policies || {},
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

                        if(Object.keys(availableKeys).length < 1) {
                            $scope.defaultOptionValue = 'No policies available';
                        } else {
                            $scope.defaultOptionValue = 'Select policy...';
                        }
                    }, function error (response) {
                        console.log(response);
                    });
            };
        }]
    };
})
.filter('signed', function () {
    return function (input) {
        input = Number(input);
        if(input > 0) {
            return '+' + input.toString(10);
        }
        return input.toString(10);
    };
});
