angular.module('AlarmDetailPage', ['AlarmsComponents', 'EucaChosenModule', 'ChartAPIModule', 'ChartServiceModule'])
.directive('alarmDetail', function () {
    return {
        restrict: 'A',
        link: function (scope, element, attrs) {
            var init = JSON.parse(attrs.alarmDetail);
            angular.extend(scope, init);
        },
        controller: ['$scope', function ($scope) {
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
        controller: ['$scope', 'CloudwatchAPI', 'ChartService', function ($scope, CloudwatchAPI, ChartService) {

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
                            unit: oData.unit || scope.unit//,
                            //preciseMetrics: preciseFormatterMetrics.indexOf(scope.metric) !== -1,
                            //maxValue: maxValue,
                            //alarms: alarms
                        });
                    });
                });
            });

        }]
    };
});
