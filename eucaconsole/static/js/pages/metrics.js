/**
 * @fileOverview CloudWatch Metrics landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('MetricsPage', ['LandingPage', 'CloudWatchCharts', 'EucaConsoleUtils'])
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
        vm.initPage = function(facets) {
            emptyFacets = JSON.parse(eucaUnescapeJson(facets));
        };
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
            items.forEach(function(metric) {
                if (metric_facet.opt_list.indexOf(metric.metric_name) === -1) {
                    metric_facet.opt_list.push(metric.metric_name);
                    metric_facet.options.push({'key':metric.metric_name, 'label':metric.metric_name});
                }
                metric.resources.forEach(function(res) {
                    if (resource_facet.opt_list.indexOf(res.res_id) === -1) {
                        resource_facet.opt_list.push(res.res_id);
                        resource_facet.options.push({'key':res.res_id, 'label':res.res_id});
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
            console.log("facets = "+JSON.stringify(facets));
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
    })
;

