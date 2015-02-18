/**
 * @fileOverview Instance Monitoring page JS
 * @requires AngularJS
 *
 */

angular.module('InstanceMonitoring', ['EucaConsoleUtils'])
    .controller('InstanceMonitoringCtrl', function ($scope, $http, $timeout, eucaUnescapeJson, eucaHandleError) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.instanceId = options.instance_id;
            $scope.cloudwatchApiUrl = options.cloudwatch_api_url;
            $(document).ready(function () {
               $scope.initCharts();
            });
        };
        $scope.initCharts = function () {
            // TODO: Convert to Angular directive for CW charts
            $('.cwchart').each(function () {
                var chartElem = $(this);
                var chartElemId = chartElem.attr('id');
                var metric = chartElem.attr('data-metric');
                var duration = chartElem.attr('data-duration');
                var unit = chartElem.attr('data-unit');
                var params = {
                    'ids': chartElem.attr('data-ids'),
                    'metric': metric,
                    'duration': duration,
                    'unit': unit
                };
                var endpointUrl = $scope.cloudwatchApiUrl + '?' + $.param(params);
                $http.get(endpointUrl).success(function(oData) {
                    var results = oData ? oData.results : '';
                    var chart = nv.models.lineChart()
                        .margin({left: 80})  //Adjust chart margins to give the x-axis some breathing room.
                        .useInteractiveGuideline(true)
                        .showYAxis(true)
                        .showXAxis(true)
                    ;
                    chart.xScale(d3.time.scale());
                    chart.xAxis.tickFormat(function(d) {
                        // TODO: Convert UTC timestamp to local time
                        return d3.time.format('%m/%d %H:%M %p')(new Date(d));
                    });
                    if (unit === 'Percent') {
                        chart.forceY([0, 100]);  // Set proper y-axis range for percentage units
                    }
                    chart.yAxis.axisLabel(unit).tickFormat(d3.format('.02f'));
                    d3.select('#' + chartElemId).datum(results).call(chart);
                    nv.utils.windowResize(chart.update);
                }).error(function (oData, status) {
                    eucaHandleError(oData, status);
                });
            });
        };
    })
;

