angular.module('AlarmDetailPage', [
    'AlarmsComponents', 'EucaChosenModule', 'ChartAPIModule', 'ChartServiceModule',
    'AlarmServiceModule', 'AlarmActionsModule', 'ModalModule', 'CreateAlarmModal', 'EucaRoutes'
])
.directive('alarmDetail', ['eucaRoutes', function (eucaRoutes) {
    return {
        restrict: 'A',
        link: function (scope, element, attrs) {
            scope.alarm = JSON.parse(attrs.alarmDetail);
            scope.alarm.actions = scope.alarm.actions || [];
            scope.alarms = [scope.alarm];  // Delete alarm confirmation dialog expects a list of alarms
            scope.expanded = true;
            scope.alarmDimensions = scope.alarm.dimensions;  // Leveraged in delete alarm confirmation dialog
            // Need stringified form on details page (and Copy Alarm dialog) to set current dimension choice
            scope.alarm.dimensions = JSON.stringify(scope.alarm.dimensions);

            if (parseInt(attrs.invalidDimensions, 10) || 0) {
                // Handle when resource in dimensions is no longer available
                scope.alarm.dimensions = '';
            }

            eucaRoutes.getRouteDeferred('cloudwatch_alarms').then(function (path) {
                scope.redirectPath = path;
            });

            scope.$watchCollection('alarm.actions', function () {
                scope.collateActions();
            });
        },
        controller: ['$scope', '$window', 'AlarmService', 'ModalService',
        function ($scope, $window, AlarmService, ModalService) {
            var csrf_token = $('#csrf_token').val();

            $scope.saveChanges = function (event) {
                $scope.alarm.dimensions = JSON.parse($scope.alarm.dimensions);
                $scope.alarm.update = true;
                if($scope.alarmUpdateForm.$invalid || $scope.alarmUpdateForm.$pristine) {
                    var $error = $scope.alarmUpdateForm.$error;
                    Object.keys($error).forEach(function (error) {
                        $error[error].forEach(function (current) {
                            current.$setTouched();
                        });
                    });
                    return;
                }

                AlarmService.updateAlarm($scope.alarm, csrf_token, true)
                    .then(function success (response) {
                        $window.location.href = $scope.redirectPath;
                    }, function error (response) {
                        $window.location.href = $scope.redirectPath;
                    });
            };

            $scope.$on('actionsUpdated', function (event, actions) {
                $scope.alarmUpdateForm.$setDirty();
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


            $scope.deleteAlarm = function (event) {
                event.preventDefault();

                var alarms = [{
                    name: $scope.alarm.name
                }];

                AlarmService.deleteAlarms(alarms, csrf_token, true)
                    .then(function success (response) {
                        $window.location.href = $scope.redirectPath;
                    }, function error (response) {
                        Notify.failure(response.data.message);
                    }); 
            };

            $scope.copyAlarm = function () {
                ModalService.openModal('copyAlarm');
            };

            $scope.collateActions = function () {
                var targets = {
                    ALARM: 'alarm_actions',
                    INSUFFICIENT_DATA: 'insufficient_data_actions',
                    OK: 'ok_actions'
                };
                $scope.alarm.insufficient_data_actions = [];
                $scope.alarm.alarm_actions = [];
                $scope.alarm.ok_actions = [];

                $scope.alarm.actions.forEach(function (action) {
                    var target = targets[action.alarm_state];
                    $scope.alarm[target].push(action.arn);
                });
            };
        }]
    };
}])
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
            $scope.$watch('dimensions', function (newVal, oldVal) {
                if(!newVal) {
                    return;
                }
                var parsedDims = angular.isObject(newVal) ? newVal : JSON.parse(newVal);
                var resourceLabel = '';
                var resourceLabels = [];
                var dimensionField = angular.element('form[name="alarmUpdateForm"]').find('[name="dimensions"]');
                var selectedDimField = dimensionField.find('[selected]');
                if (selectedDimField.length && newVal === $scope.dimensions) {
                    resourceLabel = selectedDimField.text();
                }
                if (newVal !== oldVal) {
                    resourceLabel = dimensionField.find("[value='" + newVal + "']").text();
                }
                if (!resourceLabel) {
                    angular.forEach(parsedDims, function (val, key) {
                        if (key !== '$$hashkey') {
                            resourceLabels.push(key + ' = ' + val);
                        }
                    });
                    resourceLabel = resourceLabels.join(', ');
                }
                var dimensions = [{
                    'dimensions': parsedDims,
                    'label': resourceLabel
                }];

                CloudwatchAPI.getChartData({
                    metric: $scope.metric,
                    dimensions: JSON.stringify(dimensions),
                    namespace: $scope.namespace,
                    duration: $scope.duration,
                    statistic: $scope.statistic,
                    unit: $scope.unit
                }).then(function(oData) {
                    var results = oData ? oData.results : '';
                    var maxValue = oData.max_value || 100;
                    if (!results.values.length) {
                        ChartService.resetChart('.metric-chart');
                    }
                    ChartService.renderChart($scope.target, results, {
                        unit: oData.unit || $scope.unit,
                        metric: $scope.metric,
                        maxValue: maxValue
                    });
                });
            });
        }]
    };
});
