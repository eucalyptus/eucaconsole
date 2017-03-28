/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview controller for metric graph page for mobile
 * @requires AngularJS, jQuery
 *
 */

angular.module('MetricGraphPage', ['CloudWatchCharts'])
    .controller('MetricsCtrl', function ($scope, $timeout, eucaUnescapeJson, eucaHandleError, ModalService) {
        // parse graph pre-selection
        var graphParams = "";
        var params = $.url().param();
        if (params.graph !== undefined) {
            // parse graph params
            $scope.graph = purl("?"+atob(params.graph)).param();
            $scope.graph.dimensions = JSON.parse($scope.graph.dimensions);
            if ($scope.graph.stat !== undefined) {
                if ($scope.graph.duration !== undefined) {
                    $scope.$broadcast("cloudwatch:updateLargeGraphParams", $scope.graph.stat, parseInt($scope.graph.period), parseInt($scope.graph.duration));
                }
                else {
                    $scope.$broadcast("cloudwatch:updateLargeGraphParams", $scope.graph.stat, parseInt($scope.graph.period), undefined, new Date($scope.graph.startTime), new Date($scope.graph.endTime));
                }
            }
        }
        $scope.$on('cloudwatch:refreshLargeChart', function ($event, stat, period, timeRange, duration, startTime, endTime) {
            graphParams = "&stat="+stat+"&period="+period;
            if (timeRange == "relative") {
                graphParams += "&duration="+duration;
            }
            else {
                graphParams += "&startTime="+startTime.toUTCString()+"&endTime="+endTime.toUTCString();
            }
        });
        function getChartEncoding(chart) {
            return "metric="+chart.metric+"&dimensions="+JSON.stringify(chart.dimensions)+graphParams;
        }
        $scope.copyUrl = function(chart) {
            var chartString = getChartEncoding(chart);
            chartString = chartString+"&namespace="+chart.namespace+"&unit="+chart.unit;
            var url = window.location.href;
            if (url.indexOf("?") > -1) {
                url = url.split("?")[0];
            }
            if (url.indexOf("#") > -1) {
                url = url.split("#")[0];
            }
            $scope.graphURL = url+"?graph="+btoa(chartString);
            $("#metrics-copy-url-modal").foundation("reveal", "open");
            $timeout(function() {
                $(".metrics-url-field").select();
            }, 500);
        };
        $scope.showCreateAlarm = function(metric) {
            var dims = {}; 
            names = [];
            metric.dimensions.forEach(function(val) {
                if (names.length > 0) {
                    names.push(' - ');
                }
                names.push(val.label);
                Object.keys(val.dimensions).forEach(function(res_type) {
                    var res_id = val.dimensions[res_type];
                    if (dims[res_type] === undefined) {
                        dims[res_type] = [res_id];
                    }
                    else {
                        dims[res_type].push(res_id);
                    }
                });
            });
            names = names.join('');
            $scope.metricForAlarm = Object.assign({}, metric);
            $scope.metricForAlarm.dimensions = dims;
            $scope.metricForAlarm.names = names;
            $timeout(function() {
                ModalService.openModal('createAlarm');
            });
        };
    })
;
