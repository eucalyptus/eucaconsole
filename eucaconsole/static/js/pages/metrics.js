/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview CloudWatch Metrics landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('MetricsPage', ['LandingPage', 'CloudWatchCharts', 'EucaConsoleUtils', 'smart-table', 'angular.filter', 'CreateAlarmModal', 'ModalModule'])
    .directive('splitbar', function () {
        var pageElement = angular.element(document.body.parentElement);
        return {
            restrict: 'A',
            link: function (scope, element, attrs, ctrl) {
                var topContainer = element.parent().children().first();
                element.on('mousedown', function(e) {
                    pageElement.on('mousemove', function(event) {
                        var diff = element[0].getBoundingClientRect().top - event.clientY;
                        var rect = topContainer[0].getBoundingClientRect();
                        topContainer.height(rect.height - diff);
                    });
                });
                pageElement.on('mouseup', function(e) {
                    pageElement.off('mousemove');
                });
            }
        };
    })
    .controller('MetricsCtrl', function ($scope, $http, $timeout, eucaUnescapeJson, eucaHandleError, ModalService, lpModelService) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        var vm = this;
        var categoryIndex = {};
        var itemNamesUrl;
        var graphParams = "";
        if (!String.prototype.repeat) {
          String.prototype.repeat = function(count) {
            'use strict';
            var str = '' + this;
            var rpt = '';
            for (;;) {
              if ((count & 1) == 1) {
                rpt += str;
              }
              count >>>= 1;
              if (count === 0) {
                break;
              }
              str += str;
            }
            return rpt;
          };
        }
        vm.initPage = function(itemNamesEndpoint, categoriesJson) {
            itemNamesUrl = itemNamesEndpoint;
            var categories = JSON.parse(categoriesJson);
            categories.forEach(function(val, idx) {
                categoryIndex[val] = idx;
            });
        };
        function enableInfiniteScroll() {
            var splitTop = $(".split-top");
            splitTop.scroll(function() {
                if (splitTop.scrollTop() + splitTop.innerHeight() >= splitTop[0].scrollHeight) {
                    $scope.$broadcast("showMore");
                }
            });
        }
        function fetchResNames(ids, res_type) {
            var data = "csrf_token="+$('#csrf_token').val()+"&restype="+res_type;
            ids.forEach(function(id) {
                data = data + "&id="+id;
            });
            $http({method:'POST', url:itemNamesUrl, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}
            ).then( function success(oData) {
                var results = oData.data ? oData.data.results : [];
                vm.items.forEach(function(item) {
                    if (item.resources !== undefined) {
                        item.resources.forEach(function(res) {
                            if (results[res.res_id] !== undefined) {
                                res.res_name = results[res.res_id][0];
                                res.res_short_name = results[res.res_id][1];
                            }
                        });
                    }
                });
            }, function error(errData) {
                eucaHandleError(errData.statusText, errData.status);
            });
        }
        $scope.$on('itemsLoaded', function($event, items) {
            vm.items = items;
            var resource_list, option_list, instances, images, volumes, params;
            // clear previous filters
            resource_list = [];
            items.forEach(function(metric, idx) {
                if (metric.heading === true) {
                    option_list = [];
                    return;
                }
                metric.resources.forEach(function(res) {
                    if (resource_list.indexOf(res.res_id) === -1) {
                        resource_list.push(res.res_id);
                    }
                });
            });
            instances = resource_list.filter(function(res) {
                return res.substring(0, 2) == "i-";
            });
            if (instances.length > 0) {
                fetchResNames(instances, 'instance');
            }
            images = resource_list.filter(function(res) {
                return res.substring(0, 4) == "emi-";
            });
            if (images.length > 0) {
                fetchResNames(images, 'image');
            }
            volumes = resource_list.filter(function(res) {
                return res.substring(0, 4) == "vol-";
            });
            if (volumes.length > 0) {
                fetchResNames(volumes, 'volume');
            }
            // set sticky table headers
            $('table.table').stickyTableHeaders({scrollableArea: $(".split-top")});
            // parse graph pre-selection
            params = $.url().param();
            if (params.graph !== undefined) {
                // parse graph params
                var graph = purl("?"+atob(params.graph)).param();
                graph.dimensions = JSON.parse(graph.dimensions);
                items.forEach(function(metric, idx) {
                    if (metric.heading === true) return;
                    if (metric.metric_name == graph.metric) {
                        // check dimensions
                        graph.dimensions.forEach(function(dim) {
                            if (metric.resources.length === 0 && Object.keys(dim).length === 0) {
                                metric.selected = true;
                            }
                            if (metric.resources.length > 0 && metric.resources.every(function(res) {
                                    return (dim[res.res_type] === res.res_id);
                                })) {
                                metric.selected = true;
                            }
                        });
                    }
                });
                if (graph.stat !== undefined) {
                    if (graph.duration !== undefined) {
                        $scope.$broadcast("cloudwatch:updateLargeGraphParams", graph.stat, parseInt(graph.period), parseInt(graph.duration));
                    }
                    else {
                        $scope.$broadcast("cloudwatch:updateLargeGraphParams", graph.stat, parseInt(graph.period), undefined, new Date(graph.startTime), new Date(graph.endTime));
                    }
                }
            }
            enableInfiniteScroll();
        });
        $scope.$on('cloudwatch:refreshLargeChart', function ($event, stat, period, timeRange, duration, startTime, endTime) {
            graphParams = "&stat="+stat+"&period="+period;
            if (timeRange == "relative") {
                graphParams += "&duration="+duration;
            }
            else {
                graphParams += "&startTime="+startTime.toUTCString()+"&endTime="+endTime.toUTCString();
            }
        });
        vm.clearSelections = function() {
            vm.items.forEach(function(metric) {
                metric.selected = false;
            });
        };
        vm.clearThisChart = function(charts) {
            charts.forEach(function(metric) {
                metric.selected = false;
            });
        };
        vm.sortGetters = {
            resources: function(value, descending) {
                if (descending === undefined) {
                    var headResources = $("tr>th:nth-of-type(2)");
                    descending = headResources.hasClass("st-sort-ascent");
                }
                var idx = ""+categoryIndex[value.cat_name];
                if (descending) {
                    idx = Object.keys(categoryIndex).length - idx;
                }
                idx = " ".repeat(3-(""+idx).length) + idx;
                var sortVal = (value.heading === true && value.res_ids === undefined || value.res_ids.length === 0) ? undefined : (value.resources[0].res_short_name !== undefined ? value.resources[0].res_short_name : value.res_ids[0]);
                if (value.heading === true || sortVal === undefined) {
                    if (descending) {
                        return idx + "z".repeat(200);
                    }
                    else {
                        return idx + " ".repeat(200);
                    }
                }
                else {
                    return idx + sortVal + " ".repeat(200 - sortVal.length);
                }
            },
            metric_name: function(value, descending) {
                if (descending === undefined) {
                    var headMetricName = $("tr>th:nth-of-type(3)");
                    descending = headMetricName.hasClass("st-sort-ascent");
                }
                var idx = ""+categoryIndex[value.cat_name];
                if (descending) {
                    idx = Object.keys(categoryIndex).length - idx;
                }
                idx = " ".repeat(3-(""+idx).length) + idx;
                if (value.heading === true) {
                    if (descending) {
                        return idx + "z".repeat(200);
                    }
                    else {
                        return idx + " ".repeat(200);
                    }
                }
                else {
                    return idx + value.metric_name + " ".repeat(30 - value.metric_name.length);
                }
                return value;
            }
        };
        vm.gridSorter = function(metric) {
            var sortBy = lpModelService.getSortBy();
            var descending = false;
            if (sortBy[0] == '-') {
                descending = true;
                sortBy = sortBy.substring(1);
            }
            if (sortBy == "metric_name") {
                return vm.sortGetters.metric_name(metric, descending);
            }
            if (sortBy == "res_name") {
                return vm.sortGetters.resources(metric, descending);
            }
        };
        vm.isDescending = function() {
            return lpModelService.isDescending();
        };
        vm.chartDimensions = function(chart) {
            var ret = [];
            chart.forEach(function(row) {
                var label = '';
                var dims = {};
                row.resources.forEach(function(res) {
                    label = label + res.res_name + " ";
                    dims[res.res_type] = res.res_id;
                });
                ret.push({'label': label, 'dimensions':dims});
            });
            return ret;
        };
        function getChartEncoding(chart) {
            var metric = '';
            var dims = [];
            if (Array.isArray(chart)) {
                chart.forEach(function(val) {
                    var tmp = {};
                    val.resources.forEach(function(res) {
                        tmp[res.res_type] = res.res_id;
                    });
                    dims.push(tmp);
                });
                metric = chart[0].metric_name;
            }
            else {
                var tmp = {};
                chart.resources.forEach(function(res) {
                    tmp[res.res_type] = res.res_id;
                });
                dims.push(tmp);
                metric = chart.metric_name;
            }
            return "metric="+metric+"&dimensions="+JSON.stringify(dims)+graphParams;
        }
        vm.copyUrl = function(chart) {
            var chartString = getChartEncoding(chart);
            var url = window.location.href;
            if (url.indexOf("?") > -1) {
                url = url.split("?")[0];
            }
            if (url.indexOf("#") > -1) {
                url = url.split("#")[0];
            }
            vm.graphURL = url+"?graph="+btoa(chartString);
            $("#metrics-copy-url-modal").foundation("reveal", "open");
            $timeout(function() {
                $(".metrics-url-field").select();
            }, 500);
        };
        vm.showCreateAlarm = function(metric) {
            var dims = {}; 
            if (!Array.isArray(metric)) {
                metric = [metric];
            }
            names = [];
            metric.forEach(function(row) {
                row.resources.forEach(function(res) {
                    if (names.length > 0) {
                        names.push(' - ');
                    }
                    names.push(res.res_name);
                    if (dims[res.res_type] === undefined) {
                        dims[res.res_type] = [res.res_id];
                    }
                    else {
                        dims[res.res_type].push(res.res_id);
                    }
                });
            });
            names = names.join('');
            $scope.metricForAlarm = {};
            // core piece of Object.assign polyfill to replace missing call in IE11
            for (var key in metric[0]) {
              $scope.metricForAlarm[key] = metric[0][key];
            }
            $scope.metricForAlarm.dimensions = dims;
            $scope.metricForAlarm.names = names;
            $timeout(function() {
                ModalService.openModal('createAlarm');
            });
        };
        vm.showGraphForItem = function(url, item) {
            var chartString = "metric="+item.metric_name+"&dimensions="+JSON.stringify(vm.chartDimensions([item]))+graphParams;
            chartString = chartString+"&namespace="+item.namespace+"&unit="+item.unit;
            window.location = url+"?graph="+btoa(chartString);
        };
    })
;

