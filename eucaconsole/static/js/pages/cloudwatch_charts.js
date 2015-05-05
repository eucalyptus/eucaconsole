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
.controller('CloudWatchChartsCtrl', function ($scope, eucaUnescapeJson, eucaOptionsArray) {
    var vm = this;
    vm.duration = 3600;  // Default duration value is one hour
    vm.largeChartDuration = 3600;
    vm.largeChartGranularity = 300;
    vm.metricTitleMapping = {};
    vm.chartsList = [];
    vm.granularityChoices = [];
    vm.originalDurationGranularitiesMapping = {};
    vm.durationGranularitiesMapping = {};
    vm.largeChartMetric = '';
    vm.largeChartLoading = false;
    vm.initController = initController;
    vm.setDurationGranularitiesOptions = setDurationGranularitiesOptions;
    vm.handleDurationChange = handleDurationChange;
    vm.submitMonitoringForm = submitMonitoringForm;
    vm.refreshCharts = refreshCharts;
    vm.refreshLargeChart = refreshLargeChart;

    function initController(optionsJson) {
        var options = JSON.parse(eucaUnescapeJson(optionsJson));
        vm.metricTitleMapping = options.metric_title_mapping;
        vm.chartsList = options.charts_list;
        vm.originalDurationGranularitiesMapping = options.duration_granularities_mapping;
        vm.durationGranularitiesMapping = setDurationGranularitiesOptions(options.duration_granularities_mapping);
        vm.granularityChoices = vm.durationGranularitiesMapping[vm.largeChartDuration];
        emptyLargeChartDialogOnOpen();
    }

    function setDurationGranularitiesOptions(mapping) {
        // Convert duration : value/label mapping to a form compatible with ng-options
        var optionsMapping = {};
        angular.forEach(Object.keys(mapping), function (duration) {
            optionsMapping[duration] = eucaOptionsArray(mapping[duration]);
        });
        return optionsMapping;
    }

    function handleDurationChange() {
        vm.granularityChoices = vm.durationGranularitiesMapping[vm.largeChartDuration];
        if (!vm.granularityChoices[vm.largeChartDuration]) {
            // Avoid empty granularity choice when duration is modified
            vm.largeChartGranularity = vm.originalDurationGranularitiesMapping[vm.largeChartDuration][0][0];
        }
        vm.refreshLargeChart();
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

    function emptyLargeChartDialogOnOpen() {
        var chartModal = $('#large-chart-modal');
        chartModal.on('open.fndtn.reveal', function () {
            chartModal.find('#large-chart').empty();
        });
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
        var parentCtrl = scope.$parent.chartsCtrl;
        var cloudwatchApiUrl = '/cloudwatch/api';  // Fine to hard-code this here since it won't likely change
        var largeChart = options.largeChart || false;
        var chartElemId = largeChart ? 'large-chart' : scope.elemId;
        if (largeChart) {
            parentCtrl.largeChartLoading = true;
            if (scope.metric !== parentCtrl.largeChartMetric) {
                // Workaround refreshLargeChart event firing multiple times to avoid multi-chart display in dialog
                return false;
            }
            // Granularity is user-selectable in large chart, so don't auto-adjust on the server
            options.params.adjustGranularity = 0;
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
            parentCtrl.largeChartLoading = false;
        }).error(function (oData, status) {
            eucaHandleError(oData, status);
        });
    }

    function linkFunc(scope, element, attrs) {
        var chartModal = $('#large-chart-modal');
        var chartWrapper = element.closest('.chart-wrapper');
        // Display large chart on small chart click
        chartWrapper.on('click', function () {
            var parentCtrl = scope.$parent.chartsCtrl;
            // Granularity (period) defaults to 5 min, so no need to pass it here
            var options = {
                'params': {
                    'ids': attrs.ids,
                    'idType': attrs.idType,
                    'metric': attrs.metric,
                    'duration': attrs.duration,
                    'unit': attrs.unit,
                    'statistic': attrs.statistic
                },
                'largeChart': true
            };
            parentCtrl.largeChartMetric = attrs.metric;
            parentCtrl.selectedChartTitle = parentCtrl.metricTitleMapping[attrs.metric];
            parentCtrl.largeChartDuration = parentCtrl.duration;
            parentCtrl.largeChartStatistic = attrs.statistic || 'Average';
            chartModal.foundation('reveal', 'open');
            $timeout(function () {
                renderChart(scope, options);
            });
            scope.$on('cloudwatch:refreshLargeChart', function () {
                $timeout(function () {
                    options.params.duration = parentCtrl.largeChartDuration;
                    options.params.statistic = parentCtrl.largeChartStatistic;
                    options.params.period = parentCtrl.largeChartGranularity;
                    renderChart(scope, options);
                });
            });
        });

        // Handle visibility of loading indicators
        scope.$watch('chartLoading', function (newVal) {
            var loadingElem = element.closest('.chart-wrapper').find('.busy');
            if (newVal) {  // Chart is loading, so display progress indicator
                loadingElem.show();
            } else {
                loadingElem.hide();
            }
        });
    }
})
;
