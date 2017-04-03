/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Usage Reports JS
 * @requires AngularJS and jQuery
 *
 */
angular.module('InstanceUsageModule', ['EucaConsoleUtils', 'MagicSearch', 'ReportingServiceModule'])
.directive('datepicker', function () {
    return {
        require: 'ngModel',
        restrict: 'A',
        scope: {
            format: "@",
        },
        link: function(scope, element, attrs){
            if(typeof(scope.format) == "undefined"){ scope.format = "yyyy/mm/dd"; }
            var endDate = new Date();
            $(element).fdatepicker({format: scope.format, pickTime: false, endDate:endDate}).on('changeDate', function(ev){
                scope.$apply(function() {
                    ngModel.$setViewValue(ev.date);
                });
            });
        }
    }; 
})
.directive('instanceUsage', function() {
    return {
        restrict: 'A',
        controller: ['$scope', '$http', '$httpParamSerializer', '$timeout', 'eucaHandleError', 'ReportingService',
            function ($scope, $http, $httpParamSerializer, $timeout, eucaHandleError, ReportingService) {
                var vm = this;
                vm.values = {
                    granularity: 'Hourly',
                    timePeriod: 'lastWeek',
                    fromDate: '',
                    toDate: '',
                    groupBy: ''
                };
                vm.isUpdating = false;
                vm.isDownloading = false;
                vm.updateUsage = function ($event) {
                    $event.preventDefault();
                    vm.loadInstanceData();
                };
                vm.usageData = [];
                vm.loadInstanceData = function() {
                    // use reports service to load montly report data
                    vm.isUpdating = true;
                    ReportingService.getInstanceUsage(vm.values.granularity, vm.values.timePeriod,
                        vm.values.fromDate, vm.values.toDate, vm.values.groupBy).then(
                    function success(result) {
                            vm.isUpdating = false;
                            vm.usageData.length = 0;
                            result.results.forEach(function(val) {
                                vm.usageData.push(val);
                            });
                        },
                        function error(errData) {
                            vm.isUpdating = false;
                            eucaHandleError(errData.data.message, errData.status);
                        });
                };
                vm.loadInstanceData();
                vm.downloadUsage = function ($event) {
                    $event.preventDefault();
                    if ($scope.instanceReportForm.$invalid) {
                        return false;
                    }
                    vm.isDownloading = true;
                    params = {
                        'granularity': vm.values.granularity,
                        'timePeriod': vm.values.timePeriod,
                        'fromTime': vm.values.fromDate,
                        'toTime': vm.values.toDate,
                        'groupBy': vm.values.groupBy
                    };
                    var url = '/reporting-api/instanceusage?' + $httpParamSerializer(params);
                    $.generateFile({
                        csrf_token: $('#csrf_token').val(),
                        filename: 'not-used', // let the server set this
                        content: 'none',
                        script: url
                    });
                    $timeout(function() {
                        vm.isDownloading = false;
                    }, 3000);
                };
            }
        ],
        controllerAs: 'instanceusage'
    };
})
.directive('usageBarChart', function() {
    return {
        restrict: 'A',
        scope: {
            data: "=ngModel",
        },
        controller: ['$scope', function($scope) {
            $scope.chart = undefined;
            console.log("graph model is :"+$scope.data);
            nv.addGraph(function() {
                $scope.chart = nv.models.multiBarChart()
                  .reduceXTicks(true)   //If 'false', every single x-axis tick label will be rendered.
                  .rotateLabels(0)      //Angle to rotate x-axis labels.
                  .groupSpacing(0.1)    //Distance between each group of bars.
                  .showControls(false)
                ;
                $scope.chart.multibar.stacked(true);

                $scope.chart.xAxis
                    .tickFormat(function(d) { return d3.time.format('%m/%d %H:%M')(new Date(d)); });

                $scope.chart.yAxis
                    .tickFormat(d3.format(',.1f'));

                d3.select('svg')
                    .datum($scope.data)
                    .call($scope.chart);
                nv.utils.windowResize($scope.chart.update);

                return $scope.chart;
            });
            $scope.$watch('data', function(newVal, oldVal) {
                if (newVal == oldVal) return;
                d3.select('.usage-chart svg')
                    .datum(newVal)
                    .call($scope.chart);
                nv.utils.windowResize($scope.chart.update);
            }, true);
        }]
    };
});
