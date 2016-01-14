/**
 * @fileOverview CloudWatch Metrics landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('MetricsPage', ['LandingPage', 'CloudWatchCharts', 'EucaConsoleUtils', 'smart-table'])
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
    .controller('MetricsCtrl', function ($scope, $timeout, eucaUnescapeJson) {
        var vm = this;
        var emptyFacets = [];
        var categoryIndex = {};
        var headResources;
        var headMetricName;
        vm.initPage = function(facets) {
            emptyFacets = JSON.parse(eucaUnescapeJson(facets));
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
        $scope.$on('itemsLoaded', function($event, items) {
            vm.items = items;
            // clear previous filters
            vm.clearFacetFilters();
            var facets = emptyFacets;
            var metric_facet = facets.find(function(elem) {
                return elem.name == 'metric_name';
            });
            var resource_facet = facets.find(function(elem) {
                return elem.name == 'res_ids';
            });
            var resource_type_facet = facets.find(function(elem) {
                return elem.name == 'res_types';
            });
            // create temp lists for simpler tests within loop
            metric_facet.opt_list = [];
            resource_facet.opt_list = [];
            resource_type_facet.opt_list = [];
            categoryIndex = {};
            items.forEach(function(metric, idx) {
                if (metric.heading === true) {
                    // record category indexes to help with sort
                    categoryIndex[metric.cat_name] = Object.keys(categoryIndex).length;
                    return;
                }
                if (metric_facet.opt_list.indexOf(metric.metric_name) === -1) {
                    metric_facet.opt_list.push(metric.metric_name);
                    metric_facet.options.push({'key':metric.metric_name, 'label':metric.metric_name});
                }
                metric.resources.forEach(function(res) {
                    if (resource_facet.opt_list.indexOf(res.res_id) === -1) {
                        resource_facet.opt_list.push(res.res_id);
                        resource_facet.options.push({'key':res.res_id, 'label':res.res_id, 'res_types':res.res_type});
                    }
                    if (resource_type_facet.opt_list.indexOf(res.res_type) === -1) {
                        resource_type_facet.opt_list.push(res.res_type);
                        resource_type_facet.options.push({'key':res.res_type, 'label':res.res_type});
                    }
                });
            });
            // prune those lists since we have facet options now
            metric_facet.opt_list = undefined;
            resource_facet.opt_list = undefined;
            resource_type_facet.opt_list = undefined;
            $scope.$broadcast("facets_updated", facets);
            // set sticky table headers
            $('table.table').stickyTableHeaders({scrollableArea: $(".split-top")});
        });
        vm.clearSelections = function() {
            vm.items.forEach(function(metric) {
                metric._selected = false;
            });
        };
        vm.clearFacetFilters = function() {
            vm.items.forEach(function(metric) {
                metric._hide = false;
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
    })
;

