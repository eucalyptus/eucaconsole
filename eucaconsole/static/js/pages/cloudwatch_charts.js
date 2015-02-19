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
            'metric': '@metric',
            'duration': '@duration',
            'unit': '@unit',
            'statistic': '@statistic'
        },
        controller: function ($scope, $http, eucaHandleError) {
            var cloudwatchApiUrl = '/cloudwatch/api';  // Fine to hard-code this here since it won't likely change
            $scope.initChart = function() {
                var params = {
                    'ids': $scope.ids,
                    'metric': $scope.metric,
                    'duration': $scope.duration,
                    'unit': $scope.unit,
                    'statistic': $scope.statistic
                };
                var endpointUrl = cloudwatchApiUrl + '?' + $.param(params);
                $http.get(endpointUrl).success(function(oData) {
                    var results = oData ? oData.results : '';
                    var chart = nv.models.lineChart()
                        .margin({left: 80})
                        .useInteractiveGuideline(true)
                        .showYAxis(true)
                        .showXAxis(true)
                    ;
                    chart.xScale(d3.time.scale());
                    chart.xAxis.tickFormat(function(d) {
                        // TODO: Convert UTC timestamp to local time
                        return d3.time.format('%m/%d %H:%M %p')(new Date(d));
                    });
                    if ($scope.unit === 'Percent') {
                        chart.forceY([0, 100]);  // Set proper y-axis range for percentage units
                    }
                    chart.yAxis.axisLabel($scope.unit).tickFormat(d3.format('.02f'));
                    d3.select('#' + $scope.elemId).datum(results).call(chart);
                    nv.utils.windowResize(chart.update);
                }).error(function (oData, status) {
                    eucaHandleError(oData, status);
                });
            };
            $scope.initChart();
        }
    };
})
;
