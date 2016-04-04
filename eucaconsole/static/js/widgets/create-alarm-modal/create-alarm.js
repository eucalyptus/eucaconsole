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
            };

            scope.resourceType = attrs.resourceType;
            scope.resourceId = attrs.resourceId;
            scope.resourceName = attrs.resourceName;

            scope.$on('modal:close', function (event, name) {
                if(name == 'createAlarm') {
                    scope.resetForm();
                }
            });

            MetricService.getMetrics(scope.resourceType, scope.resourceId)
                .then(function (metrics) {
                    scope.metrics = metrics || [];

                    scope.alarm.metric = (function (metrics, defaultMetric) {
                        var metric;
                        for(var i = 0; i < metrics.length; i++ ) {
                            metric = metrics[i];
                            if(metric.name == defaultMetric) {
                                break;
                            }
                        }
                        return metric;
                    }(scope.metrics, attrs.defaultMetric));

                    scope.alarm.statistic = attrs.defaultStatistic;
                    scope.alarm.comparison = '>=';

                    defaults.metric = scope.alarm.metric;
                });

            scope.checkNameCollision();
        },
        controller: ['$scope', '$rootScope', 'AlarmService', 'ModalService', function ($scope, $rootScope, AlarmService, ModalService) {
            $scope.alarm = {};
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
                    return alarm.name == name;
                });

                if(collision) {
                    name = $scope.alarmName(count + 1);
                }

                return name;
            };

            $scope.createAlarm = function () {
                if($scope.createAlarmForm.$invalid) {
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
                $scope.createAlarmForm.$setPristine();
                $scope.createAlarmForm.$setUntouched();
                $scope.checkNameCollision();
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
}]);
