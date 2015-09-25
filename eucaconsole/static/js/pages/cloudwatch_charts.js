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
    vm.emptyMessages = {};
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
    vm.emptyChartCount = 0;
    vm.forceZeroBaselineMetrics = [ // Anchor chart to zero for the following metrics
        'NetworkIn', 'NetworkOut', 'DiskReadBytes', 'DiskReadOps',
        'DiskWriteBytes', 'DiskWriteOps', 'RequestCount', 'Latency', 'HealthyHostCount', 'UnHealthyHostCount',
        'HTTPCode_ELB_4XX', 'HTTPCode_ELB_5XX', 'HTTPCode_Backend_2XX', 'HTTPCode_Backend_3XX',
        'HTTPCode_Backend_4XX', 'HTTPCode_Backend_5XX'
    ];
    vm.displayZeroChartMetrics = [  // Display a zero chart rather than an empty message for the following metrics
        'HTTPCode_ELB_4XX', 'HTTPCode_ELB_5XX', 'HTTPCode_Backend_2XX', 'HTTPCode_Backend_3XX',
        'HTTPCode_Backend_4XX', 'HTTPCode_Backend_5XX'
    ];
    vm.specifyZonesMetrics = [  // Pass availability zones for certain metrics
        'HealthyHostCount', 'UnHealthyHostCount'
    ];

    function initController(optionsJson) {
        var options = JSON.parse(eucaUnescapeJson(optionsJson));
        vm.metricTitleMapping = options.metric_title_mapping;
        vm.chartsList = options.charts_list;
        vm.availabilityZones = options.availability_zones || [];
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
        vm.emptyMessages = {};
        vm.emptyChartCount = 0;
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
            'namespace': '@namespace',
            'duration': '@duration',
            'unit': '@unit',
            'statistic': '@statistic',
            'empty': '@empty'
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
            'namespace': scope.namespace,
            'duration': scope.duration,
            'unit': scope.unit,
            'statistic': scope.statistic
        };
        params.tzoffset = (new Date()).getTimezoneOffset();
        if (parentCtrl.specifyZonesMetrics.indexOf(scope.metric) !== -1) {
            params.zones = parentCtrl.availabilityZones.join(',');
        }
        $http({
            'url': cloudwatchApiUrl,
            'method': 'GET',
            'params': params
        }).success(function(oData) {
            scope.chartLoading = false;
            if (typeof oData === 'string' && oData.indexOf('<html') > -1) {
                $('#timed-out-modal').foundation('reveal', 'open');
            }
            var results = oData ? oData.results : '';
            var displayZeroChart = parentCtrl.displayZeroChartMetrics.indexOf(scope.metric) !== -1;
            var emptyResultsCount = 0;
            results.forEach(function (resultSet) {
                if (resultSet.values.length === 0) {
                    emptyResultsCount += 1;
                }
            });
            if (!displayZeroChart && emptyResultsCount === results.length && scope.empty && !largeChart) {
                parentCtrl.emptyMessages[scope.metric] = scope.empty;
                parentCtrl.emptyChartCount += 1;
                return true;
            }
            if (largeChart && emptyResultsCount === results.length) {
                // Remove existing chart when there are no results in large chart modal to avoid lingering empty msg
                d3.select('#' + chartElemId).selectAll("svg > *").remove();
            }
            var unit = oData.unit || scope.unit;
            var yformatter = '.0f';
            var preciseFormatterMetrics = ['Latency'];
            var chart = nv.models.lineChart()
                .margin({left: 68, right: 38})
                .useInteractiveGuideline(true)
                .showYAxis(true)
                .showXAxis(true)
            ;
            if (displayZeroChart && results.length === 1 &&  results[0].values.length === 0) {
                // Pad chart with zero data where appropriate
                results = [{
                    key: scope.metric,
                    values: [{x: new Date().getTime(), y: 0}]
                }];
            }
            chart.xScale(d3.time.scale());
            chart.xAxis.tickFormat(function(d) {
                return d3.time.format('%m/%d %H:%M')(new Date(d));
            });
            if (scope.unit === 'Percent') {
                chart.forceY([0, 100]);  // Set proper y-axis range for percentage units
            }
            if (parentCtrl.forceZeroBaselineMetrics.indexOf(scope.metric) !== -1) {
                chart.forceY([0, 10]);  // Anchor chart to zero baseline
            }
            if (preciseFormatterMetrics.indexOf(scope.metric) !== -1) {
                yformatter = '.2f';
            }
            if (unit === 'Kilobytes') {
                yformatter = '.1f';
            } else if (unit === 'Megabytes' || unit === 'Gigabytes') {
                yformatter = '.2f';
            }
            chart.yAxis.axisLabel(unit).tickFormat(d3.format(yformatter));
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
                    'idtype': attrs.idtype,
                    'metric': attrs.metric,
                    'namespace': attrs.namespace,
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
