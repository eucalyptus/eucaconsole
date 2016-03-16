angular.module('AlarmDetailPage', [
    'AlarmsComponents', 'EucaChosenModule', 'ChartAPIModule', 'ChartServiceModule',
    'AlarmServiceModule', 'AlarmActionsModule'
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
});
