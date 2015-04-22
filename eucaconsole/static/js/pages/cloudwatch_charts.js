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
    vm.durationChoices = [];
    vm.initController = initController;
    vm.submitMonitoringForm = submitMonitoringForm;
    vm.refreshCharts = refreshCharts;

    function submitMonitoringForm() {
        document.getElementById('monitoring-form').submit();
    }

    function initController(optionsJson) {
        var options = JSON.parse(eucaUnescapeJson(optionsJson));
        angular.forEach(options.monitoring_duration_choices, function(item) {
            vm.durationChoices.push({val: item[0], label: item[1]});
        });
    }

    function refreshCharts() {
        // Broadcast message to CW charts directive controller to refresh
        $scope.$broadcast('cloudwatch:refreshCharts');
    }
})
.directive('cloudwatchChart', function($http, eucaHandleError) {
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
        var cloudwatchApiUrl = '/cloudwatch/api';  // Fine to hard-code this here since it won't likely change
        options = options || {};
        // Anchor chart to zero for the following metrics
        scope.chartLoading = true;
        var chartElemId = options.elemId || scope.elemId;
        if (options.empty) {
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
        var options = {
            'elemId': 'large-chart',
            'params': attrs,
            'chartLoading': false,  // Prevent loading indicators on parent charts page
            'empty': true  // empty chart prior to rendering
        };

        // Enable large charts
        element.closest('.chart-wrapper').on('click', function () {
            scope.$parent.chartsCtrl.selectedChart = attrs;
            var chartModal = $('#large-chart-modal');
            chartModal.foundation('reveal', 'open');
            renderChart(scope, options);
            scope.$apply();
        });

        scope.$on('refreshLargeChart', function () {
            options.duration = scope.$parent.chartsCtrl.largeChartDuration;
            renderChart(scope, options);
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
