/**
 * @fileOverview CloudWatch Metrics landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('MetricsPage', ['LandingPage', 'CloudWatchCharts', 'EucaConsoleUtils', 'smart-table', 'angular.filter'])
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
    .directive('datepicker', function () {
        return {
            require: 'ngModel',
            restrict: 'A',
            scope: { format: "=" },
            link: function(scope, element, attrs, ngModel){
                if(typeof(scope.format) == "undefined"){ scope.format = "yyyy/mm/dd hh:ii"; }
                var startDate = new Date();
                startDate.setHours(-(14 * 24));  // move back 2 weeks
                var endDate = new Date();
                $(element).fdatepicker({format: scope.format, pickTime: true, startDate:startDate, endDate:endDate}).on('changeDate', function(ev){
                    console.log("date from datepicker directive: "+ev.date);
                    scope.$apply(function(){
                        ngModel.$setViewValue(ev.date);
                    }); 
                });
            }
        }; 
    })
    .controller('MetricsCtrl', function ($scope, $http, $timeout, eucaUnescapeJson) {
        var vm = this;
        var categoryIndex = {};
        var headResources;
        var headMetricName;
        var itemNamesUrl;
        var graphParams = "";
        vm.initPage = function(itemNamesEndpoint) {
            itemNamesUrl = itemNamesEndpoint;
            enableInfiniteScroll();
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
                                res.res_name = results[res.res_id];
                            }
                        });
                    }
                });
            }, function error(errData) {
                eucaErrorHandler(errData.statusText, errData.status);
            });
        }
        $scope.$on('itemsLoaded', function($event, items) {
            vm.items = items;
            // clear previous filters
            resource_list = [];
            items.forEach(function(metric, idx) {
                if (metric.heading === true) {
                    // record category indexes to help with sort
                    categoryIndex[metric.cat_name] = Object.keys(categoryIndex).length;
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
                var graph = purl("?"+$.base64.decode(params.graph)).param();
                items.forEach(function(metric, idx) {
                    if (metric.metric_name == graph.metric) {
                        // check dimensions
                        if (metric.resources.every(function(res) {
                                return (graph.dimensions[res.res_type] === res.res_id);
                            })) {
                            metric._selected = true;
                        }
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
        });
        $scope.$on('cloudwatch:refreshLargeChart', function ($event, stat, period, timeRange, duration, startTime, endTime) {
            graphParams = "&stat="+stat+"&period="+period;
            if (timeRange == "relative") {
                graphParams += "&duration="+duration;
            }
            else {
                graphParams += "&startTime="+startTime.toUTCString()+"&endTime="+endTime.toUTCString();
            }
            //$(".nv-x g.nvd3.nv-wrap.nv-axis .tick text").detach()
            //$(".nv-x g.nvd3.nv-wrap.nv-axis .nv-axisMaxMin text").detach()
        });
        vm.clearSelections = function() {
            vm.items.forEach(function(metric) {
                metric._selected = false;
            });
        };
        vm.clearThisChart = function(charts) {
            charts.forEach(function(metric) {
                metric._selected = false;
            });
        };
        vm.sortGetters = {
            resources: function(value) {
                if (headResources === undefined) {
                    headResources = $("tr>th:nth-of-type(2)");
                }
                var decending = headResources.hasClass("st-sort-ascent");
                var idx = ""+categoryIndex[value.cat_name];
                if (decending) {
                    idx = Object.keys(categoryIndex).length - idx;
                }
                idx = " ".repeat(3-(""+idx).length) + idx;
                if (value.heading === true && value.res_ids === undefined || value.res_ids.length === 0) {
                    if (decending) {
                        return idx + "z".repeat(200);
                    }
                    else {
                        return idx + " ".repeat(200);
                    }
                }
                else {
                    //console.log(idx + value.res_ids[0] + " ".repeat(200 - value.res_ids[0].length));
                    return idx + value.res_ids[0] + " ".repeat(200 - value.res_ids[0].length);
                }
            },
            metric_name: function(value) {
                if (headMetricName === undefined) {
                    headMetricName = $("tr>th:nth-of-type(3)");
                }
                var decending = headMetricName.hasClass("st-sort-ascent");
                var idx = ""+categoryIndex[value.cat_name];
                if (decending) {
                    idx = Object.keys(categoryIndex).length - idx;
                }
                idx = " ".repeat(3-(""+idx).length) + idx;
                if (value.heading === true && value.res_ids === undefined || value.res_ids.length === 0) {
                    if (decending) {
                        return idx + "z".repeat(200);
                    }
                    else {
                        return idx + " ".repeat(200);
                    }
                }
                else {
                    //console.log(idx + value.metric_name + " ".repeat(30 - value.metric_name.length));
                    return idx + value.metric_name + " ".repeat(30 - value.metric_name.length);
                }
                return value;
            }
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
        vm.copyUrl = function(chart) {
            var dims = {};
            if (Array.isArray(chart)) {
                chart = chart[0];
            }
            chart.resources.forEach(function(res) {
                dims[res.res_type] = res.res_id;
            });
            var chart_string = "metric="+chart.metric_name+"&dimensions="+JSON.stringify(dims)+graphParams;
            var url = window.location.href;
            if (url.indexOf("?") > -1) {
                url = url.split("?")[0];
            }
            if (url.indexOf("#") > -1) {
                url = url.split("#")[0];
            }
            vm.graphURL = url+"?graph="+$.base64.encode(chart_string);
            $("#metrics-copy-url-modal").foundation("reveal", "open");
            $timeout(function() {
                $(".metrics-url-field").select();
            }, 500);
        };
    })
;

