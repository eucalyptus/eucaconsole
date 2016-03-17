angular.module('CreateAlarmModal', ['ModalModule', 'AlarmServiceModule', 'ScalingGroupsServiceModule', 'AlarmActionsModule'])
.directive('createAlarm', ['MetricService', function (MetricService) {
    return {
        restrict: 'A',
        require: 'modal',
        link: function (scope, element, attrs) {
            scope.resourceType = attrs.resourceType;
            scope.resourceId = attrs.resourceId;
            scope.resourceName = attrs.resourceName;

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
                    scope.alarm.unit = attrs.defaultUnit;
                    scope.alarm.comparison = '>=';
                });
        },
        controller: ['$scope', 'AlarmService', function ($scope, AlarmService) {
            $scope.alarm = {};
            var csrf_token = $('#csrf_token').val();

            $scope.$watchCollection('alarm', function () {
                if($scope.alarm.metric) {
                    $scope.alarm.name = $scope.alarmName();
                }
            });

            $scope.alarmName = function () {
                // Name field updates when metric selection changes,
                // unless the user has changed the value themselves.
                /*
                if($scope.createAlarm.name.$touched) {
                    return $scope.alarm.name;
                }
                */
                
                var alarm = $scope.alarm;
                var name = [
                    alarm.metric.namespace,
                    $scope.resourceName || $scope.resourceId,
                    alarm.metric.name].join(' - ');

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
                    dimensions: alarm.metric.dimensions
                }, csrf_token).then(function () {
                    console.log('blah', arguments);
                }, function () {
                    console.log('error', arguments);
                });
            };

            $scope.resetForm = function () {
            };
        }]
    };
}])
.factory('MetricService', ['$http', '$interpolate', function ($http, $interpolate) {
    var metricsUrl = $interpolate('/metrics/available/{{ resourceType }}/{{ resourceValue }}');
    var _metrics = {};

    return {
        getMetrics: function (resourceType, resourceValue) {
            if(resourceValue in _metrics) {
                return _metrics[resourceValue];
            }

            return $http({
                method: 'GET',
                url: metricsUrl({
                    resourceType: resourceType,
                    resourceValue: resourceValue
                })
            }).then(function (result) {
                if(result && result.data) {
                    _metrics[resourceValue] = result.data.metrics;
                }
                return _metrics[resourceValue];
            });
        }
    };
}]);
