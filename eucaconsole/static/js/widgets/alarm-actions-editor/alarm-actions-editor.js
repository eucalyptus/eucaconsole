angular.module('AlarmActionsModule', ['AlarmServiceModule', 'ScalingGroupsServiceModule'])
.directive('alarmActions', function () {
    return {
        restrict: 'E',
        replace: true,
        require: ['^ngModel', 'alarmActions'],
        scope: {
            allActions: '=ngModel',
            okActions: '=',
            alarmActions: '=',
            insufficientDataActions: '='
        },
        templateUrl: function (element, attributes) {
            return attributes.template;
        },
        link: function (scope, element, attrs, ctrls) {
            var modelCtrl = ctrls[0],       // Controller for ngModel
                actionsCtrl = ctrls[1];     // Controller for this directive

            scope.defaultOptionValue = 'Select policy...';

            scope.$watchCollection('action', function (newVal) {
                var validity = actionsCtrl.validate(newVal);
                modelCtrl.$setValidity('actionEditor', validity);
            });

            scope.$watchCollection('allActions', function (newVal, oldVal) {
                if(newVal != oldVal) {
                    modelCtrl.$setDirty();
                    modelCtrl.$setTouched();
                }
            });

            window.onbeforeunload = function () {
                if(scope.state === 'incomplete') {
                    return $('#warning-message-unsaved-changes').text();
                }
            };
        },
        controller: ['$scope', 'AlarmService', 'ScalingGroupsService', function ($scope, AlarmService, ScalingGroupsService) {
            var vm = this;

            ScalingGroupsService.getScalingGroups().then(function (result) {
                $scope.scalingGroups = result;
                if ($scope.scalingGroupName) {
                    $scope.resetForm();
                    $scope.updatePolicies();
                }
            });

            this.validate = function (action, callback) {
                var validity = false;

                if(action.scalingGroup === '' && action.scalingGroupPolicy === '') {
                    // Valid because empty: form valid, add action button disabled
                    $scope.state = 'empty';
                    validity = true;
                } else if(action.scalingGroup !== '' && action.scalingGroupPolicy !== '') {
                    // Valid because complete: form valid, add action button enabled
                    $scope.state = 'complete';
                    validity = true;
                } else {
                    // Invalid because incomplete: form invalid, add action button disabled
                    $scope.state = 'incomplete';
                    validity = false;
                }

                return validity;
            };

            $scope.addAction = function (evt) {
                evt.preventDefault();
                //  Do not add action if form is invalid
                if($scope.state != 'complete') {
                    return;
                }

                var policyName = $scope.action.scalingGroupPolicy,
                    policy = $scope.scalingGroupPolicies[policyName];

                //  Do not add action if duplicate
                var duplicate = $scope.allActions.some(function (current) {
                    return current.arn === policy.arn && current.alarm_state === $scope.action.alarm_state;
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
                $scope.allActions.push(action);

                $scope.updateActions();
            };

            $scope.removeAction = function ($index) {
                $scope.allActions.splice($index, 1);
                $scope.updateActions();
            };

            $scope.updateActions = function () {
                $scope.$emit('actionsUpdated', $scope.allActions);
                $scope.resetForm();
            };

            $scope.resetForm = function () {
                $scope.action = {
                    alarm_state: 'ALARM',
                    scalingGroup: '',
                    scalingGroupPolicy: ''
                };
                $scope.defaultOptionValue = 'Select policy...';
                $scope.scalingGroupPolicies = {};
            };

            $scope.policiesAvailable = function () {
                var policies = $scope.scalingGroupPolicies || {};
                return !Object.keys(policies).length;
            };

            $scope.updatePolicies = function () {
                if($scope.action.scalingGroup === '' || $scope.action.scalingGroup === undefined) {
                    $scope.action.scalingGroupPolicy = '';
                    return;
                }

                ScalingGroupsService.getPolicies($scope.action.scalingGroup)
                    .then(function success (data) {
                        var policies = data.policies || {},
                            filtered = {};

                        var availableKeys = Object.keys(policies).filter(function (key) {
                            return !$scope.allActions.some(function (action) {
                                return action.policy_name === key && action.alarm_state === $scope.action.alarm_state;
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
                        $scope.scalingGroupPolicies = {};
                        $scope.defaultOptionValue = 'No policies available';
                    });
            };
        }]
    };
})
.directive('doNotValidate', function () {
    return {
        require: ['^form', 'ngModel'],
        restrict: 'A',
        link: function (scope, element, attrs, ctrls) {
            var formCtrl = ctrls[0],
                modelCtrl = ctrls[1];

            formCtrl.$removeControl(modelCtrl);
            scope.$watch(attrs.ngModel, function () {
                modelCtrl.$setUntouched();
                modelCtrl.$setPristine();
            });
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
