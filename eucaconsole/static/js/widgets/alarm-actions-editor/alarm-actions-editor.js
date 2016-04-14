angular.module('AlarmActionsModule', ['AlarmServiceModule', 'ScalingGroupsServiceModule'])
.directive('alarmActions', function () {
    return {
        restrict: 'A',
        scope: true,
        link: function (scope, element, attrs) {
            scope.alarmId = attrs.alarmId;
            scope.alarmActions = JSON.parse(attrs.alarmActions);
            scope.defaultOptionValue = 'Select policy...';
        },
        controller: ['$scope', 'AlarmService', 'ScalingGroupsService', function ($scope, AlarmService, ScalingGroupsService) {
            ScalingGroupsService.getScalingGroups().then(function (result) {
                $scope.scalingGroups = result;
                if ($scope.scalingGroupName) {
                    $scope.resetForm();
                    $scope.updatePolicies();
                }
            });

            $scope.addAction = function () {
                //  Do not add action if form is invalid
                if($scope.alarmActionsForm.$invalid || $scope.alarmActionsForm.$pristine) {
                    return;
                }

                var policyName = $scope.action.scalingGroupPolicy,
                    policy = $scope.scalingGroupPolicies[policyName];

                //  Do not add action if duplicate
                var duplicate = $scope.alarmActions.some(function (current) {
                    return current.arn == policy.arn && current.alarm_state == $scope.action.alarm_state;
                });
                if(duplicate) {
                    return;
                }

                var action = {
                    alarm_state: $scope.action.alarm_state,
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
                $scope.$emit('actionsUpdated', $scope.alarmActions);
                $scope.resetForm();
            };

            $scope.resetForm = function () {
                $scope.action = {
                    alarm_state: 'ALARM',
                    scalingGroup: $scope.scalingGroupName || ''
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
                                return action.policy_name == key && action.alarm_state == $scope.action.alarm_state;
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
.directive('requiredIfChanged', function () {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function (scope, element, attrs, ctrl) {
            ctrl.$validators.requiredIfChanged = function (modelValue, viewValue) {
                if(ctrl.$touched && ctrl.$isEmpty(modelValue)) {
                    return false;
                }
                return true;
            };
        }
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
