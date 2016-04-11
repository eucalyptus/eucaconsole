angular.module('CreateAlarmModal', [
    'ModalModule',
    'AlarmServiceModule',
    'MetricServiceModule',
    'ScalingGroupsServiceModule',
    'AlarmActionsModule'
])
.directive('createAlarm', ['MetricService', 'AlarmService', function (MetricService, AlarmService) {
    var defaults = {};

    return {
        restrict: 'A',
        require: '^modal',
        templateUrl: function (element, attributes) {
            return attributes.template;
        },
        link: function (scope, element, attrs) {
            defaults = {
                statistic: attrs.defaultStatistic,
                metric: attrs.defaultMetric,
                comparison: '>=',
                evaluation_periods: 1,
                period: 300
            };

            var resourceDimensions = {};
            resourceDimensions[attrs.resourceType] = [attrs.resourceId];

            scope.namespace = attrs.namespace;
            scope.resourceType = attrs.resourceType;
            scope.resourceId = attrs.resourceId;
            scope.dimensions = attrs.dimensions ? JSON.parse(attrs.dimensions) : resourceDimensions;
            scope.resourceName = attrs.resourceName;
            scope.existingAlarms = [];

            scope.$on('modal:close', function (event, name) {
                if(name === 'createAlarm') {
                    scope.resetForm();
                }
            });

            if (attrs.loadmetricchoices !== 'false') {
                MetricService.getMetrics(scope.namespace, scope.resourceType, scope.resourceId)
                    .then(function (metrics) {
                        scope.metrics = metrics;

                        scope.alarm.metric = metrics.find(function(metric) {
                            return metric.name === defaults.metric;
                        });
                        scope.alarm.metric.namespace = scope.namespace;
                        scope.alarm.metric.dimensions = scope.dimensions;
                        scope.alarm.statistic = attrs.defaultStatistic;
                        scope.alarm.comparison = '>=';
                        scope.alarm.evaluation_periods = defaults.evaluation_periods;
                        scope.alarm.period = defaults.period;

                        defaults.metric = scope.alarm.metric;
                    });
            }
            else {
                // let's construct the metric object from data passed
                scope.alarm.metric = {
                    name: defaults.metric,
                    dimensions: scope.dimensions,
                };
                scope.alarm.metric.namespace = scope.namespace;
                scope.alarm.statistic = attrs.defaultStatistic;
                scope.alarm.comparison = '>=';
                scope.alarm.evaluation_periods = defaults.evaluation_periods;
                scope.alarm.period = defaults.period;
            }

            scope.checkNameCollision();
        },
        controller: ['$scope', '$rootScope', 'AlarmService', 'ModalService', function ($scope, $rootScope, AlarmService, ModalService) {
            $scope.alarm = {};
            $scope.alarm.metric = {};
            var csrf_token = $('#csrf_token').val();

            $scope.onNameChange = function () {
                $scope.createAlarmForm.name.$setTouched();
            };

            $scope.$watchCollection('alarm', function (newVal) {
                if(newVal.metric && $scope.createAlarmForm.name.$untouched) {
                    $scope.alarm.name = $scope.alarmName();
                }
            });

            $scope.alarmName = function (count) {
                // Name field updates when metric selection changes,
                // unless the user has changed the value themselves.
                count = count || 0;
                if(count > 20) {
                    $scope.createAlarmForm.name.$setValidity('uniqueName', false);
                    return $scope.alarm.name;
                }
                
                var alarm = $scope.alarm;
                var name = [
                    alarm.metric.namespace,
                    $scope.resourceName || $scope.resourceId,
                    alarm.metric.name].join(' - ');

                if(count > 0) {
                    name = name + [' (', ')'].join(count);
                }

                var collision = $scope.existingAlarms.some(function (alarm) {
                    return alarm.name === name;
                });

                if(collision) {
                    name = $scope.alarmName(count + 1);
                }

                return name;
            };

            $scope.createAlarm = function () {
                if($scope.createAlarmForm.$invalid) {
                    var $error = $scope.createAlarmForm.$error;
                    Object.keys($error).forEach(function (error) {
                        $error[error].forEach(function (current) {
                            current.$setTouched();
                        });
                    });
                    return;
                }

                var alarm = $scope.alarm;

                AlarmService.createAlarm({
                    name: alarm.name,
                    metric: alarm.metric.name,
                    namespace: alarm.metric.namespace,
                    statistic: alarm.statistic,
                    comparison: alarm.comparison,
                    threshold: alarm.threshold,
                    period: alarm.period,
                    evaluation_periods: alarm.evaluation_periods,
                    unit: alarm.unit,
                    description: alarm.description,
                    dimensions: alarm.metric.dimensions,
                    alarm_actions: alarm.alarm_actions,
                    insufficient_data_actions: alarm.insufficient_data_actions,
                    ok_actions: alarm.ok_actions
                }, csrf_token).then(function success (response) {
                    ModalService.closeModal('createAlarm');
                    Notify.success(response.data.message);
                    $rootScope.$broadcast('alarmStateView:refreshList');
                }, function error (response) {
                    ModalService.closeModal('createAlarm');
                    Notify.failure(response.data.message);
                });
            };

            $scope.$on('actionsUpdated', function (event, actions) {
                var targets = {
                    ALARM: 'alarm_actions',
                    INSUFFICIENT_DATA: 'insufficient_data_actions',
                    OK: 'ok_actions'
                };
                $scope.alarm.insufficient_data_actions = [];
                $scope.alarm.alarm_actions = [];
                $scope.alarm.ok_actions = [];

                actions.forEach(function (action) {
                    var target = targets[action.alarm_state];
                    $scope.alarm[target].push(action.arn);
                });
            });

            $scope.resetForm = function () {
                $scope.alarm = angular.copy(defaults);
                $scope.checkNameCollision();
                $scope.createAlarmForm.$setPristine();
                $scope.createAlarmForm.$setUntouched();
            };

            $scope.checkNameCollision = function () {
                $scope.existingAlarms = [];
                AlarmService.getAlarmsForResource($scope.resourceId, $scope.resourceType)
                    .then(function (alarms) {
                        $scope.existingAlarms = alarms;
                        $scope.alarm.name = $scope.alarmName();
                    });
            };
        }]
    };
}])
.directive('uniqueName', function () {
    return {
        restrict: 'A',
        require: ['ngModel', '^createAlarm'],
        link: function (scope, element, attrs, ctrls) {
            var modelCtrl = ctrls[0],
                formCtrl = ctrls[1];

            modelCtrl.$validators.uniqueName = function (modelValue, viewValue) {
                return !scope.existingAlarms.some(function (alarm) {
                    return alarm.name === viewValue;
                });
            };

        }
    };
});
