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
.controller('CloudWatchChartsCtrl', function ($scope, eucaUnescapeJson) {
    var vm = this;
    vm.duration = 3600;  // Default duration value is one hour
    vm.largeChartDuration = 3600;
    vm.metricTitleMapping = {};
    vm.initController = initController;
    vm.submitMonitoringForm = submitMonitoringForm;
    vm.refreshCharts = refreshCharts;
    vm.refreshLargeChart = refreshLargeChart;

    function initController(optionsJson) {
        var options = JSON.parse(eucaUnescapeJson(optionsJson));
        vm.metricTitleMapping = options.metric_title_mapping;
    }

    function submitMonitoringForm() {
        document.getElementById('monitoring-form').submit();
    }

    function refreshCharts() {
        // Broadcast message to CW charts directive controller to refresh
        $scope.$broadcast('cloudwatch:refreshCharts');
    }

    function refreshLargeChart() {
        $scope.$broadcast('cloudwatch:refreshLargeChart');
    }

})
.directive('cloudwatchChart', function($http, $timeout, eucaHandleError) {
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
        link: linkFunc,
        controller: ChartController
    };

    function ChartController($scope, $timeout) {
        renderChart($scope);
        $scope.$on('cloudwatch:refreshCharts', function () {
            $timeout(function () {
                renderChart($scope);
            });
        });
    }

    function renderChart(scope, options) {
        options = options || {};
        scope.chartLoading = !options.largeChart;
        var cloudwatchApiUrl = '/cloudwatch/api';  // Fine to hard-code this here since it won't likely change
        var largeChart = options.largeChart || false;
        var chartElemId = largeChart ? 'large-chart' : scope.elemId;
        if (largeChart) {
            $('#' + chartElemId).empty();
        }
        var params = options.params || {
            'ids': scope.ids,
            'idtype': scope.idtype,
            'metric': scope.metric,
            'duration': scope.duration,
            'unit': scope.unit,
            'statistic': scope.statistic
        };
        params.tzoffset = (new Date()).getTimezoneOffset();
        $http({
            'url': cloudwatchApiUrl,
            'method': 'GET',
            'params': params
        }).success(function(oData) {
            scope.chartLoading = false;
            var results = oData ? oData.results : '';
            var unit = oData.unit || scope.unit;
            // Anchor chart to zero for the following metrics
            var forceZeroBaselineMetrics = [
                'NetworkIn', 'NetworkOut', 'DiskReadBytes', 'DiskReadOps',
                'DiskWriteBytes', 'DiskWriteOps'
            ];
            var chart = nv.models.lineChart()
                .margin({left: 68})
                .useInteractiveGuideline(true)
                .showYAxis(true)
                .showXAxis(true)
            ;
            chart.xScale(d3.time.scale());
            chart.xAxis.tickFormat(function(d) {
                return d3.time.format('%m/%d %H:%M')(new Date(d));
            });
            if (scope.unit === 'Percent') {
                chart.forceY([0, 100]);  // Set proper y-axis range for percentage units
            }
            if (forceZeroBaselineMetrics.indexOf(scope.metric) !== -1) {
                chart.forceY([0, 100]);  // Anchor chart to zero baseline
            }
            chart.yAxis.axisLabel(unit).tickFormat(d3.format('.0f'));
            d3.select('#' + chartElemId).datum(results).call(chart);
            nv.utils.windowResize(chart.update);
        }).error(function (oData, status) {
            eucaHandleError(oData, status);
        });
    }

    function linkFunc(scope, element, attrs) {
        var chartModal = $('#large-chart-modal');
        // Display large chart on small chart click
        element.closest('.chart-wrapper').on('click', function () {
            var parentCtrl = scope.$parent.chartsCtrl;
            var options = {
                'params': attrs,
                'largeChart': true
            };
            parentCtrl.selectedChartTitle = parentCtrl.metricTitleMapping[attrs.metric];
            parentCtrl.largeChartDuration = parentCtrl.duration;
            parentCtrl.largeChartStatistic = attrs.statistic || 'Average';
            chartModal.foundation('reveal', 'open');
            renderChart(scope, options);
            scope.$apply();
            scope.$on('cloudwatch:refreshLargeChart', function () {
                $timeout(function () {
                    options.params.duration = parentCtrl.largeChartDuration;
                    options.params.statistic = parentCtrl.largeChartStatistic;
                    renderChart(scope, options);
                });
            });
        });

        // Handle visibility of loading indicators
        scope.$watch('chartLoading', function (newVal) {
            var loadingElem = element.find('text.loading');
            if (newVal) {  // Chart is loading, so display progress indicator
                loadingElem.attr('visibility', 'visible');
            } else {
                loadingElem.attr('visibility', 'hidden');
            }
        });
    }
})
;
