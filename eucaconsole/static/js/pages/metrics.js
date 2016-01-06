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
        vm.ec2SubMetric = 'instance';
        vm.elbSubMetric = 'elb';
        var emptyFacets = [];
        vm.initPage = function(facets) {
            emptyFacets = JSON.parse(eucaUnescapeJson(facets));
        };
        vm.filterMetrics = function(metricGroup) {
            if (metricGroup.name === 'ebs') {
                // do nothing
            }
            else if (metricGroup.name === 'ec2') {
                if (metricGroup.unfiltered === undefined) {
                    metricGroup.unfiltered = metricGroup.metrics;
                }
                metricGroup.metrics = metricGroup.unfiltered.filter(function(val) {
                    if (vm.ec2SubMetric === 'instance' && val.resources[0].res_type == 'InstanceId')
                        return true;
                    else if (vm.ec2SubMetric === 'image' && val.resources[0].res_type == 'ImageId')
                        return true;
                    if (vm.ec2SubMetric === 'instancetype' && val.resources[0].res_type == 'InstanceType')
                        return true;
                    if (vm.ec2SubMetric === 'allinstances' && val.resources[0].res_type == 'AutoScalingGroupName')
                        return true;
                    return false;
                });
            }
            else if (metricGroup.name === 'scalinggroup') {
                // do nothing
            }
            else if (metricGroup.name === 'elb') {
                if (metricGroup.unfiltered === undefined) {
                    metricGroup.unfiltered = metricGroup.metrics;
                }
                metricGroup.metrics = metricGroup.unfiltered.filter(function(val) {
                    if (val.resources.length == 1) {
                        if (vm.elbSubMetric === 'elb' && val.resources[0].res_type == 'LoadBalancerName')
                            return true;
                        else if (vm.elbSubMetric === 'zone' && val.resources[0].res_type == 'AvailabilityZone')
                            return true;
                    }
                    else
                        if (vm.elbSubMetric === 'elbzone' && val.resources[1].res_type == 'LoadBalancerName' && val.resources[0].res_type == 'AvailabilityZone')
                            return true;
                    return false;
                });
            }
            return metricGroup.metrics;
        };
        $scope.$on('itemsLoaded', function($event, items) {
            vm.items = items;
            // clear previous filters
            vm.clearFacetFilters();
            var facets = emptyFacets;
            var metric_facet = facets.find(function(elem) {
                return elem.name == 'metric';
            });
            var resource_facet = facets.find(function(elem) {
                return elem.name == 'resource';
            });
            var resource_type_facet = facets.find(function(elem) {
                return elem.name == 'resource_type';
            });
            // create temp lists for simpler tests within loop
            metric_facet.opt_list = [];
            resource_facet.opt_list = [];
            resource_type_facet.opt_list = [];
            items.forEach(function(category) {
                category.metrics.forEach(function(metric) {
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
            });
            // prune those lists since we have facet options now
            metric_facet.opt_list = undefined;
            resource_facet.opt_list = undefined;
            resource_type_facet.opt_list = undefined;
            $scope.$broadcast("facets_updated", facets);
        });
        /*  Returns true if only 1 item selected
         */
        vm.singleSelection = function() {
            var ret = false;
            var done = false;
            if (vm.items) {
                vm.items.some(function(category) {
                    category.metrics.some(function(metric) {
                        if (metric._selected === true) {
                            if (ret === true) {
                                // fail fast if 2nd item selected
                                ret = false;
                                done = true;
                            }
                            else {
                                ret = true;
                                $scope.selection = metric;
                            }
                        }
                        return done;
                    });
                    return done;
                });
            }
            if (!ret) $scope.selection = undefined;
            return ret;
        };
        vm.numberFound = function() {
            if (vm.items) {
                return vm.items.reduce(function(prevVal, currVal) {
                    return prevVal + currVal.metrics.filter(function(val) { return !val._hide; }).length;
                }, 0);
            }
            else {
                return 0;
            }
        };
        vm.clearFacetFilters = function() {
            vm.items.forEach(function(category) {
                category.metrics.forEach(function(metric) {
                    metric._hide = false;
                });
            });
        };
        /*  Apply facet filtering
         *  to apply text filtering, call searchFilterItems instead
         */
        var matchByFacet = function(facet, val) {
            if (typeof val === "string") {
                if (facet.indexOf(val) > -1 ||
                    facet.indexOf(val.toLowerCase()) > -1) {
                    return true;
                }
            }
            return false;
        };
        var filterByFacet = function(item, facet, key) {
            // handle special case of empty facet value, match all
            if (facet.indexOf("") > -1) {
                return true;
            }
            if (key == "metric")
                val = item.metric_name;
            if (key == "resource")
                val = item.resources[0].res_id;
            if (key == "resource_type")
                val = item.resources[0].res_type;
            if (val === undefined || val === null) {
                return false;
            }
            if (Array.isArray(val)) {
                for (var i=0; i<val.length; i++) {
                    return matchByFacet(facet, val[i]);
                }
            }
            else {
                return matchByFacet(facet, val);
            }
        };
        $scope.facetFilterItems = function(query) {
            var url = window.location.href;
            // clear previous filters
            vm.items.forEach(function(val) {
                val.metrics.forEach(function(metric) {
                    metric._hide = true;
                });
            });
            if (query !== undefined && query.length !== 0) {
                // prepare facets by grouping
                var tmp = query.split('&').sort();
                var facets = {};
                angular.forEach(tmp, function(item) {
                    var facet = item.split('=');
                    if (this[facet[0]] === undefined) {
                        this[facet[0]] = [];
                    }
                    this[facet[0]].push(facet[1]);
                }, facets);
                // filter results
                var metricsFunc = function(metric) {
                    if (filterByFacet(metric, facets[key], key)) {
                        metric._hide = false;
                        var linkIdSelector = "a[id='" + this.name + "']";
                        if (expandSections.indexOf(linkIdSelector) === -1) {
                            expandSections.push(linkIdSelector);
                        }
                    }
                };
                var categoryFunc = function(category) {
                    category.metrics.forEach(metricsFunc, category);
                };
                var expandSections = [];
                for (var key in facets) {
                    vm.items.forEach(categoryFunc);
                }
                // close open expandos
                $timeout(function() {
                    $("i[class='table-expando-open']").trigger("click");
                    expandSections.forEach(function(selector) {
                        $(selector).trigger("click");
                    });
                });
            }
            else {
                vm.clearFacetFilters();
            }
            //$scope.searchFilterItems();
        };
        $scope.$on('searchUpdated', function($event, query) {
            $scope.facetFilterItems(query);
        });
        $scope.$on('textSearch', function($event, text, filter_keys) {
        });
    })
;

