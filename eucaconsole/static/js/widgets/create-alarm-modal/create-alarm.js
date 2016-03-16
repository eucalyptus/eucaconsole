angular.module('CreateAlarmModal', ['AlarmServiceModule'])
.directive('modal', ['ModalService', function (ModalService) {
    return {
        restrict: 'A',
        template: '<div class="modal-bg"></div><div class="modal-content"><a ng-click="closeModal()" class="close-modal">×</a><ng-transclude></ng-transclude></div>',
        transclude: true,
        link: function (scope, element, attrs) {
            scope.modalName = attrs.modal;
            ModalService.registerModal(scope.modalName, element);
        },
        controller: ['$scope', function ($scope) {
            $scope.closeModal = function () {
                ModalService.closeModal($scope.modalName);
            };
        }]
    };
}])
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
                console.log($scope.createAlarmForm);
                console.log('alarm at controller', alarm);

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
                    dimensions: alarm.dimensions
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
}])
.factory('ModalService', function () {
    var _modals = {};

    function registerModal (name, element) {
        if(name in _modals) {
            console.error('Modal with name ', name, ' already registered.');
            return;
        }
        _modals[name] = element;
    }

    function openModal (name) {
        var modal = _modals[name];
        if(!modal) {
            return;
        }

        modal.addClass('open');
    }

    function closeModal (name) {
        var modal = _modals[name];
        if(!modal) {
            return;
        }

        modal.removeClass('open');
    }

    return {
        openModal: openModal,
        closeModal: closeModal,
        registerModal: registerModal
    };
});
