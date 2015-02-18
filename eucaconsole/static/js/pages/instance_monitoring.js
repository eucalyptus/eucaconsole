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
                        .margin({left: 100})  //Adjust chart margins to give the x-axis some breathing room.
                        .useInteractiveGuideline(true)
                        .showYAxis(true)
                        .showXAxis(true)
                    ;
                    chart.xScale(d3.time.scale());
                    chart.xAxis = {
                        axisLabel: 'Date',
                        tickFormat: function(d){
                            return  d3.time.format('%Y-%m-%dT%H:%M:%S')(new Date(d))
                        }
                    };
                    chart.yAxis.axisLabel(metric).tickFormat(d3.format('.02f'));
                    d3.select('#' + chartElemId).datum(results).call(chart);
                }).error(function (oData, status) {
                    eucaHandleError(oData, status);
                });
            });
        }
    })
;

