/**
 * @fileOverview AngularJS CloudWatch chart directive
 * @requires AngularJS, D3, nvd3.js
 *
 * Examples:
 * Fetch average CPU utilization percentage for instance 'i-foo' for the past hour
 * <svg cloudwatch-chart="" id="cwchart-cpu" class="cwchart" ids="i-foo" idtype="InstanceId"
 *      metric="CPUUtilization"duration="3600" unit="Percent" statistic="Average" />
 *
 */

angular.module('CloudWatchCharts', ['EucaConsoleUtils'])
.directive('cloudwatchChart', function() {
    return {
        restrict: 'A',  // Restrict to attribute since container element must be <svg>
        scope: {
            'elemId': '@id',
            'ids': '@ids',
            'idtype': '@idtype',
            'metric': '@metric',
            'duration': '@duration',
            'unit': '@unit',
            'statistic': '@statistic'
        },
        controller: function ($scope, $http, $timeout, eucaHandleError) {
            var cloudwatchApiUrl = '/cloudwatch/api';  // Fine to hard-code this here since it won't likely change
            $scope.renderChart = function() {
                // Anchor chart to zero for the following metrics
                $scope.chartLoading = true;
                var params = {
                    'ids': $scope.ids,
                    'idtype': $scope.idtype,
                    'metric': $scope.metric,
                    'duration': $scope.duration,
                    'unit': $scope.unit,
                    'statistic': $scope.statistic,
                    'tzoffset': (new Date()).getTimezoneOffset()
                };
                $http({
                    'url': cloudwatchApiUrl,
                    'method': 'GET',
                    'params': params
                }).success(function(oData) {
                    $scope.chartLoading = false;
                    var results = oData ? oData.results : '';
                    var unit = oData.unit || $scope.unit;
                    var forceZeroBaselineMetrics = [
                        'NetworkIn', 'NetworkOut', 'DiskReadBytes', 'DiskReadOps',
                        'DiskWriteBytes', 'DiskWriteOps'
                    ];
                    var chart = nv.models.lineChart()
                        .margin({left: 80})
                        .useInteractiveGuideline(true)
                        .showYAxis(true)
                        .showXAxis(true)
                    ;
                    chart.xScale(d3.time.scale());
                    chart.xAxis.tickFormat(function(d) {
                        return d3.time.format('%m/%d %H:%M %p')(new Date(d));
                    });
                    if ($scope.unit === 'Percent') {
                        chart.forceY([0, 100]);  // Set proper y-axis range for percentage units
                    }
                    if (forceZeroBaselineMetrics.indexOf($scope.metric) !== -1) {
                        chart.forceY([0, 1000]);  // Anchor chart to zero baseline
                    }
                    chart.yAxis.axisLabel(unit).tickFormat(d3.format('.02f'));
                    d3.select('#' + $scope.elemId).datum(results).call(chart);
                    nv.utils.windowResize(chart.update);
                }).error(function (oData, status) {
                    eucaHandleError(oData, status);
                });
            };
            $scope.renderChart();
            $scope.$on('cloudwatch:refreshCharts', function () {
                $timeout(function () {
                    $scope.renderChart();
                });
            });
        },
        link: function (scope, element, attrs) {
            scope.$watch('chartLoading', function (newVal) {
                var loadingElem = element.find('text.loading');
                if (newVal) {  // Chart is loading, so display progress indicator
                    loadingElem.attr('visibility', 'visible');
                } else {
                    loadingElem.attr('visibility', 'hidden');
                }
            });
        }
    };
})
;
