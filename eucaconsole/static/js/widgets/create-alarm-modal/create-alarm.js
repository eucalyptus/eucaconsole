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
        require: ['^modal', 'createAlarm'],
        templateUrl: function (element, attributes) {
            return attributes.template;
        },
        link: function (scope, element, attrs, ctrls) {
            var modalCtrl = ctrls[0],
                createAlarmCtrl = ctrls[1];

            var modalName;

            createAlarmCtrl.initializeModal(attrs);

            scope.$on('modal:open', function (event, name) {
                modalName = name;
                scope.modalName = name;
                createAlarmCtrl.initializeModal(attrs);
            });
            scope.$on('modal:close', function (event, name) {
                if(name === modalName) {
                    scope.resetForm(name);
                }
            });
        },
        controller: ['$scope', '$rootScope', 'AlarmService', 'ModalService', function ($scope, $rootScope, AlarmService, ModalService) {
            var vm = this;
            $scope.alarm = {};
            $scope.namespaces = [];
            var csrf_token = $('#csrf_token').val();
            var loadBalancers = [];

            $scope.onNameChange = function () {
                $scope.createAlarmForm.name.$setTouched();
            };

            $scope.$watchCollection('alarm', function (newVal) {
                if(newVal.metric && $scope.createAlarmForm.name.$untouched) {
                    $scope.alarm.name = $scope.alarmName();
                }
            });

            $scope.alarmName = function (count) {
                // Set alarm name to blank on Copy Alarm dialog
                if ($scope.alarm.name === '') {
                    return $scope.alarm.name;
                }
                // Name field updates when metric selection changes,
                // unless the user has changed the value themselves.
                count = count || 0;
                if(count > 20) {
                    $scope.createAlarmForm.name.$setValidity('uniqueName', false);
                    return $scope.alarm.name;
                }

                var alarm = $scope.alarm;
                var resName = $scope.resourceName || $scope.resourceId;
                if (resName === undefined) {
                    resName = [];
                    Object.keys($scope.dimensions).forEach(function(key) {
                        if (resName.length > 0) {
                            resName.push(' - ');
                        }
                        if (angular.isArray($scope.dimensions[key])) {
                            // Skip Angular $$hashkey in $scope.dimensions
                            resName.push($scope.dimensions[key].join(' - '));
                        }
                    });
                    resName = resName.join('');
                }
                var name = [
                    alarm.metric.namespace,
                    resName,
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

            this.composeAlarmMetric = function (attrs) {
                if (!$scope.namespace.match(',')) {  // Avoid breaking namespace when multiple NS are passed to directive
                    $scope.alarm.metric.namespace = $scope.namespace;
                }
                $scope.alarm.dimensions = attrs.alarmName ? JSON.stringify($scope.dimensions) : $scope.dimensions;
                if ($scope.invalidDimensions) {
                    $scope.alarm.dimensions = '';
                }
                $scope.alarm.statistic = $scope.alarm.statistic ? $scope.alarm.statistic : attrs.defaultStatistic;
                $scope.alarm.comparison = '>=';
                $scope.alarm.evaluation_periods = defaults.evaluation_periods;
                $scope.alarm.period = defaults.period;

                if (attrs.alarmName && !attrs.alarmsLanding) {
                    $('#dimensions-select').chosen({'width': '100%', search_contains: true});
                } else {
                    $scope.updateStaticDimensions($scope.alarm);
                    $scope.checkNameCollision();
                }
            };

            this.initializeModal = function(attrs) {
                defaults = {
                    statistic: attrs.defaultStatistic,
                    metric: attrs.defaultMetric,
                    comparison: '>=',
                    evaluation_periods: 1,
                    period: 300
                };

                $scope.title = attrs.title || 'Create Alarm';
                $scope.hideAlarmActions = attrs.hideAlarmActions || false;
                $scope.editDimensions = attrs.editDimensions || false;
                $scope.dimensionChoices = [];
                $scope.alarmsLanding = attrs.alarmsLanding || false;
                if (attrs.editDimensions && !attrs.alarmsLanding) {
                    // Build dimension choices for Copy Alarm on alarm details page
                    $scope.dimensionChoices = JSON.parse(attrs.dimensionChoices);
                }
                $scope.existingAlarms = [];
                if(attrs.alarmName) {
                    AlarmService.getAlarm(attrs.alarmName)
                        .then(function (res) {
                            var alarm = res.alarm;
                            alarm.name = '';
                            vm.initializeForCopy(alarm, attrs);
                            var nameField = angular.element('[name="createAlarmForm"]').find('[name="name"]');
                            nameField.focus();
                            $scope.createAlarmForm.name.$touched = false;
                        });
                } else {
                    this.initializeForCreate(attrs);
                }
            };

            this.initializeForCopy = function (alarm, attrs) {
                var parsedDimensionChoices = null;
                var selectedChoices = [];
                var allDimensionChoices = [];
                var stdDimensionNamespaces = ['AWS/EC2', 'AWS/ELB', 'AWS/EBS'];
                if (attrs.alarmName) {
                    $scope.title = 'Create alarm like ' + attrs.alarmName;
                }
                $scope.alarm = alarm;
                $scope.alarm.name = '';
                $scope.alarm.dimensions = alarm.dimensions;
                $scope.dimensions = alarm.dimensions;
                $scope.invalidDimensions = false;
                $scope.namespace = alarm.namespace;
                $scope.resourceType = attrs.resourceType;
                $scope.resourceId = attrs.resourceId;
                if (attrs.editDimensions && attrs.alarmsLanding) {
                    // Handle dimension choices on alarms landing page
                    parsedDimensionChoices = JSON.parse(attrs.dimensionChoices);
                    if (stdDimensionNamespaces.indexOf(alarm.namespace) === -1) {
                        // Alarms with custom metric/namespace
                        parsedDimensionChoices = JSON.parse(attrs.dimensionChoices);
                        stdDimensionNamespaces.forEach(function (namespace) {
                            Array.prototype.push.apply(allDimensionChoices, parsedDimensionChoices[namespace]);
                        });
                        $scope.dimensionChoices = allDimensionChoices;
                    } else {
                        // Alarms with standard namespace
                        $scope.dimensionChoices = parsedDimensionChoices[alarm.namespace];
                    }
                    selectedChoices = $scope.dimensionChoices.filter(function (item) {
                        return !!item.selected || item.value === JSON.stringify($scope.alarm.dimensions);
                    });
                    if (selectedChoices.length === 0) {
                        // Handle when resource in dimensions is no longer available (e.g. instance was terminated)
                        $scope.invalidDimensions = true;
                    }
                }
                finishInit(attrs);
            };

            this.initializeForCreate = function (attrs) {
                $scope.scalingGroupName = attrs.scalingGroupName || '';
                $scope.namespace = attrs.namespace;
                $scope.resourceType = attrs.resourceType;
                $scope.resourceId = attrs.resourceId;
                $scope.dimensions = attrs.dimensions ? JSON.parse(attrs.dimensions) : undefined;
                if ($scope.dimensions === undefined) {
                    $scope.dimensions = {};
                    $scope.dimensions[$scope.resourceType] = [$scope.resourceId];
                }
                $scope.resourceName = attrs.resourceName;
                finishInit(attrs);
            };

            var finishInit = function(attrs) {
                if (attrs.loadMetricChoices !== 'false') {
                    MetricService.getMetrics($scope.namespace, $scope.dimensions)
                        .then(function (results) {
                            $scope.metrics = results.metrics;
                            $scope.namespaces = results.namespaces;

                            // Used for updating scaling group dimensions when ASG has one or more ELBs
                            if (results.namespaces.indexOf('AWS/ELB') !== -1 && attrs.loadBalancers) {
                                loadBalancers = JSON.parse(attrs.loadBalancers);
                            }

                            $scope.alarm.metric = results.metrics.find(function(metric) {
                                return metric.name === defaults.metric;
                            });

                            defaults.metric = $scope.alarm.metric;
                            vm.composeAlarmMetric(attrs);
                        });
                }
                else {
                    // let's construct the metric object from data passed
                    $scope.alarm.metric = {
                        name: defaults.metric,
                        unit: attrs.unit
                    };

                    vm.composeAlarmMetric(attrs);
                }
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
                    unit: alarm.metric.unit,
                    description: alarm.description,
                    dimensions: alarm.dimensions,
                    alarm_actions: alarm.alarm_actions,
                    insufficient_data_actions: alarm.insufficient_data_actions,
                    ok_actions: alarm.ok_actions
                }, csrf_token).then(function success (response) {
                    ModalService.closeModal($scope.modalName || 'createAlarm');
                    Notify.success(response.data.message);
                    $rootScope.$broadcast('alarmStateView:refreshList', {name: alarm.name});
                }, function error (response) {
                    ModalService.closeModal($scope.modalName || 'createAlarm');
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

            $scope.resetForm = function (modalName) {
                if (modalName !== 'copyAlarm') {
                    $scope.alarm = angular.copy(defaults);
                    $scope.checkNameCollision();
                }
                $scope.createAlarmForm.$setPristine();
                $scope.createAlarmForm.$setUntouched();
            };

            $scope.checkNameCollision = function () {
                $scope.existingAlarms = [];
                AlarmService.getAlarmsForDimensions($scope.dimensions)
                    .then(function success(alarms) {
                        $scope.existingAlarms = alarms;
                        $scope.alarm.name = $scope.alarmName();
                    });
            };

            $scope.updateStaticDimensions = function (alarm) {
                var metricNS = alarm.metric.namespace;
                var dimensionKeys = Object.keys(alarm.dimensions);
                if (metricNS.match(/^AWS\//)) {  // Skip custom metrics
                    // Adjust dimensions where necessary on Scaling group monitoring and policy pages
                    if ($scope.resourceType === 'AutoScalingGroupName') {
                        if (metricNS === 'AWS/ELB' && dimensionKeys.indexOf('AutoScalingGroupName') !== -1 && loadBalancers.length) {
                            $scope.alarm.dimensions = {
                                'LoadBalancerName': loadBalancers
                            };
                        } else if (metricNS === 'AWS/EC2' && $scope.resourceId) {
                            $scope.alarm.dimensions = {
                                'AutoScalingGroupName': [$scope.resourceId]
                            };
                        }
                    }
                }
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
