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
    .controller('MetricsCtrl', function ($scope, eucaUnescapeJson) {
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
            items.forEach(function(val) {
                val.metrics.forEach(function(metric) {
                    if (metric_facet.options.indexOf(metric.metric_name) === -1) {
                        metric_facet.options.push(metric.metric_name);
                    }
                    metric.resources.forEach(function(res) {
                        if (resource_facet.options.indexOf(res.res_id) === -1) {
                            resource_facet.options.push(res.res_id);
                        }
                        if (resource_type_facet.options.indexOf(res.res_type) === -1) {
                            resource_type_facet.options.push(res.res_type);
                        }
                    });
                });
            });
            $scope.$broadcast("facets_updated", facets);
            /*
            search_facets = [
                {'name': 'metric', 'label': _(u"Metric name"), 'options': [
                    {'key': 'tbd', 'label': _("TBD")},
                ]},
                {'name': 'resource', 'label': _(u"Resource type"), 'options': [
                    {'key': 'tbd', 'label': _("TBD")},
                ]}
            ]
            */
        });
    })
;

