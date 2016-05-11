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

angular.module('CloudWatchCharts', ['EucaConsoleUtils', 'ChartAPIModule', 'ChartServiceModule', 'CreateAlarmModal', 'ModalModule'])
.directive('datepicker', function () {
    return {
        require: 'ngModel',
        restrict: 'A',
        scope: {
            format: "@",
        },
        link: function(scope, element, attrs){
            if(typeof(scope.format) == "undefined"){ scope.format = "yyyy/mm/dd hh:ii"; }
            var startDate = new Date();
            startDate.setHours(-(14 * 24));  // move back 2 weeks
            var endDate = new Date();
            $(element).fdatepicker({format: scope.format, pickTime: true, startDate:startDate, endDate:endDate}).on('changeDate', function(ev){
                scope.$apply(function() {
                    ngModel.$setViewValue(ev.date);
                });
            });
        }
    }; 
})
.controller('CloudWatchChartsCtrl', function ($scope, eucaUnescapeJson, eucaOptionsArray, ModalService) {
    var vm = this;
    vm.duration = 3600;  // Default duration value is one hour
    vm.largeChartStatistic = "Sum";
    vm.largeChartDuration = 3600;
    vm.largeChartGranularity = 300;
    vm._largeChartStartTime = new Date();
    vm._largeChartStartTime.setSeconds(-vm.largeChartDuration);
    vm._largeChartEndTime = new Date();
    vm.timeRange = "relative";
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
    vm.emptyChartCount = 0;

    vm.revealCreateModal = revealCreateModal;

    vm.displayZeroChartMetrics = [  // Display a zero chart rather than an empty message for the following metrics
        'HTTPCode_ELB_4XX', 'HTTPCode_ELB_5XX', 'HTTPCode_Backend_2XX', 'HTTPCode_Backend_3XX',
        'HTTPCode_Backend_4XX', 'HTTPCode_Backend_5XX'
    ];
    vm.specifyZonesMetrics = [  // Pass availability zones for certain metrics
        'HealthyHostCount', 'UnHealthyHostCount'
    ];
    Date.prototype.datetime = function() {
        var mm = (this.getMonth()+1).toString();
        var dd = this.getDate().toString();
        var hh = this.getHours().toString();
        var ii = this.getMinutes().toString();
        return this.getFullYear() + "/" + (mm.length===2?mm:"0" + mm[0]) + "/" + (dd.length===2?dd:"0" + dd[0]) +
            " " + (hh.length===2?hh:"0" + hh[0]) + ":" + (ii.length===2?ii:"0" + ii[0]);
    };
    vm.largeChartStartTime = function(newDate) {
        //return arguments.length ? (vm._largeChartStartTime = new Date(newDate)) : vm._largeChartStartTime.datetime();
        if (arguments.length) {
            vm._largeChartStartTime = new Date(newDate);
            return vm._largeChartStartTime;
        }
        else {
            return vm._largeChartStartTime.datetime();
        }
    };
    vm.largeChartEndTime = function(newDate) {
        return arguments.length ? (vm._largeChartEndTime = new Date(newDate)) : vm._largeChartEndTime.datetime();
    };

    function initController(optionsJson) {
        var options = JSON.parse(eucaUnescapeJson(optionsJson));
        vm.metricTitleMapping = options.metric_title_mapping;
        vm.chartsList = options.charts_list;
        vm.availabilityZones = options.availability_zones || [];
        vm.originalDurationGranularitiesMapping = options.duration_granularities_mapping;
        vm.durationGranularitiesMapping = setDurationGranularitiesOptions(options.duration_granularities_mapping);
        vm.granularityChoices = vm.durationGranularitiesMapping[vm.largeChartDuration];
        vm.fullGranularityChoices = options.granularity_choices;
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
        // update absolute to match
        vm._largeChartStartTime = new Date();
        vm._largeChartStartTime.setSeconds(-vm.largeChartDuration);
        vm._largeChartEndTime = new Date();
        vm.refreshLargeChart();
    }

    vm.showLargeChart = function(title, metric, statistic, unit, namespace, ids, idtype) {
        vm.selectedChartTitle = title; // || parentCtrl.metricTitleMapping[attrs.metric];
        vm.largeChartMetric = metric;
        vm.largeChartStatistic = statistic || 'Average';
        vm.largeChartUnit = unit;
        vm.largeChartNamespace = namespace;
        vm.largeChartIds = ids;
        vm.largeChartIdType = idtype;
        vm.largeChartDuration = vm.duration;
        vm.refreshLargeChart();
        ModalService.openModal('largeChart');
    };

    function getTimeShift() {
        return (vm._largeChartEndTime.valueOf() - vm._largeChartStartTime.valueOf()) / 2000;
    }

    vm.shiftTimeLeftAllowed = function() {
        var startDate = new Date();
        startDate.setHours(-(14 * 24));  // move back 2 weeks
        var timeDiffSecs = getTimeShift();
        return new Date(vm._largeChartStartTime).setSeconds(-timeDiffSecs) > startDate;
    };

    vm.shiftTimeRightAllowed = function() {
        var timeDiffSecs = getTimeShift();
        return new Date(vm._largeChartEndTime).setSeconds(timeDiffSecs) < (new Date());
    };

    vm.shiftTimeLeft = function() {
        if (vm.shiftTimeLeftAllowed()) {
            vm.timeRange = "absolute";
            var timeDiffSecs = getTimeShift();
            vm._largeChartStartTime.setSeconds(-timeDiffSecs);
            vm._largeChartEndTime.setSeconds(-timeDiffSecs);
            vm.refreshLargeChart();
        }
    };

    vm.shiftTimeRight = function() {
        if (vm.shiftTimeRightAllowed()) {
            vm.timeRange = "absolute";
            var timeDiffSecs = getTimeShift();
            vm._largeChartStartTime.setSeconds(timeDiffSecs);
            vm._largeChartEndTime.setSeconds(timeDiffSecs);
            vm.refreshLargeChart();
        }
    };

    vm.handleAbsoluteChange = function() {
        // calculate acceptable granularities based on chosen time range
        var timeDiffSecs = (vm._largeChartEndTime.valueOf() - vm._largeChartStartTime.valueOf()) / 1000;
        vm.granularityChoices = vm.fullGranularityChoices.filter(function(choice) {
            return ((timeDiffSecs / choice[0]) <= 1440) && (choice[0] < timeDiffSecs);
        }).map(function(choice) {
            return {value: choice[0], label: choice[1]};
        });
        if (vm.largeChartGranularity < vm.granularityChoices[0].value) {
            // set to lowest if old value below lowest
            vm.largeChartGranularity = vm.granularityChoices[0].value;
        }
        var last = vm.granularityChoices.length;
        if (vm.largeChartGranularity > vm.granularityChoices[last-1].value) {
            // set to highest if old value above highest
            vm.largeChartGranularity = vm.granularityChoices[last-1].value;
        }
        vm.refreshLargeChart();
    };
    $scope.$on("cloudwatch:updateLargeGraphParams", function($event, stat, period, duration, startTime, endTime) {
        vm.largeChartStatistic = stat;
        vm.largeChartGranularity = period;
        if (duration !== undefined) {
            vm.timeRange = "relative";
            vm.largeChartDuration = duration;
        }
        else {
            vm.timeRange = "absolute";
            vm._largeChartStartTime = startTime;
            vm._largeChartEndTime = endTime;
        }
    });

    function submitMonitoringForm() {
        document.getElementById('monitoring-form').submit();
    }

    function refreshCharts(refreshOptions) {
        refreshOptions = refreshOptions || null;
        vm.emptyMessages = {};
        vm.emptyChartCount = 0;
        // Broadcast message to CW charts directive controller to refresh
        $scope.$broadcast('cloudwatch:refreshCharts', refreshOptions);
    }

    vm.refreshLargeChart = function() {
        $scope.$broadcast('cloudwatch:refreshLargeChart');
        // for external listeners
        $scope.$emit('cloudwatch:refreshLargeChart', vm.largeChartStatistic, vm.largeChartGranularity, vm.timeRange, vm.largeChartDuration, vm._largeChartStartTime, vm._largeChartEndTime);
    };

    function emptyLargeChartDialogOnOpen() {
        var chartModal = $('#large-chart-modal');
        chartModal.on('open.fndtn.reveal', function () {
            chartModal.find('#large-chart').empty();
        });
    }

    function revealCreateModal () {
        ModalService.openModal('createAlarm');
    }
})
.directive('cloudwatchChart', function($http, $timeout, CloudwatchAPI, ChartService, ModalService, eucaHandleError) {
    return {
        restrict: 'A',  // Restrict to attribute since container element must be <svg>
        scope: {
            'elemId': '@id',
            'ids': '@ids',  // takes single id, or comma-separated list (no spaces)
            'idtype': '@idtype',  // takes single type
            'dimensions': '@dimensions',  // takes array of rows, each w/ dict of dimensions (replaces ids, idtype)
            'metric': '@metric',
            'namespace': '@namespace',
            'period': '@period',
            'duration': '@duration',
            'startTime': '@startTime',
            'endTime': '@endTime',
            'unit': '@unit',
            'statistic': '@statistic',
            'title': '@title',
            'empty': '@empty',
            'large': '@large',
            'noXLabels': '@noXLabels',
            'autoLoad': '@'
        },
        link: linkFunc,
        controller: ChartController
    };

    function ChartController($scope, $timeout) {
        $scope.$on('cloudwatch:refreshCharts', function (evt, refreshOptions) {
            var doRefresh = false;
            // Conditionally refresh charts based on passed options
            if (refreshOptions) {
                if (refreshOptions.namespace === $scope.namespace) {
                    doRefresh = true;
                }
            } else {
                doRefresh = true;
            }
            if (doRefresh) {
                $timeout(function () {
                    renderChart($scope);
                });
            }
        });
        $scope.$watch('dimensions', function(newVal, oldVal) {
            if (newVal != oldVal) {
                renderChart($scope);
            }
        });
        if ($scope.large) {
            var parentCtrl = $scope.$parent.chartsCtrl;
            parentCtrl.largeChartMetric = $scope.metric;

            $scope.$on('cloudwatch:refreshLargeChart', function () {
                $timeout(function () {
                    renderChart($scope);
                });
            });
            if ($scope.autoLoad) {
                renderChart($scope);
            }
        }
        else {
            renderChart($scope);
        }
    }

    function renderChart(scope, options) {
        options = options || {};
        scope.chartLoading = !options.largeChart;
        var parentCtrl = scope.$parent.chartsCtrl;
        var largeChart = options.largeChart || false;
        if (largeChart) {
            if (scope.metric !== parentCtrl.largeChartMetric) {
                // Workaround refreshLargeChart event firing multiple
                // times to avoid multi-chart display in dialog
                return false;
            }
        }
        largeChart = options.largeChart || scope.large;
        var params = options.params || {
            'ids': scope.ids,
            'idtype': scope.idtype,
            'dimensions': scope.dimensions,
            'metric': scope.metric,
            'namespace': scope.namespace,
            'period': scope.period,
            'duration': scope.duration,
            'startTime': scope.startTime,
            'endTime': scope.endTime,
            'unit': scope.unit,
            'statistic': scope.statistic
        };
        // look for minimum set of required params
        if ((scope.ids === undefined || scope.ids === '') &&
            (scope.idtype === undefined || scope.idtype === '') &&
            (scope.dimensions === undefined || scope.dimensions === '')) {
            return;
        }
        if (largeChart) {
            parentCtrl.largeChartLoading = true;
            // Granularity is user-selectable in large chart, so don't auto-adjust on the server
            params.adjustGranularity = 0;
        }

        params.tzoffset = (new Date()).getTimezoneOffset();
        if (parentCtrl.specifyZonesMetrics.indexOf(scope.metric) !== -1) {
            params.zones = parentCtrl.availabilityZones.join(',');
        }

        CloudwatchAPI.getChartData(params).then(function(oData) {

            if (typeof oData === 'string' && oData.indexOf('<html') > -1) {
                $('#timed-out-modal').foundation('reveal', 'open');
            }

            scope.chartLoading = false;
            var results = oData ? oData.results : '';
            var maxValue = oData ? oData.max_value : 0;
            var displayZeroChart = parentCtrl.displayZeroChartMetrics.indexOf(scope.metric) !== -1;
            var emptyResultsCount = 0;
            var target = largeChart && $('#large-chart').length > 0 ? $('#large-chart').get(0) : scope.target;

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
                // Remove existing chart when there are no results in large
                // chart modal to avoid lingering empty msg
                ChartService.resetChart(target);
            }
            var preciseFormatterMetrics = ['Latency'];
            if (displayZeroChart && results.length === 1 &&  results[0].values.length === 0) {
                // Pad chart with zero data where appropriate
                results = [{
                    key: scope.metric,
                    values: [{x: new Date().getTime(), y: 0}],
                    color: '#2ad2c9'
                }];
            }

            ChartService.resetChart(target);
            var chart = ChartService.renderChart(target, results, {
                unit: oData.unit || scope.unit,
                preciseMetrics: preciseFormatterMetrics.indexOf(scope.metric) !== -1,
                maxValue: maxValue,
                noXLabels: scope.noXLabels
            });
            nv.utils.windowResize(chart.update);
            parentCtrl.largeChartLoading = false;
        }, function (oData, status) {
            eucaHandleError(oData, status);
        });
    }

    function linkFunc(scope, element, attrs) {

        scope.target = element[0];

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
