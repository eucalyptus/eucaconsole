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
            var metrics = [];
            items.forEach(function(val) {
                val.metrics.forEach(function(metric) {
                    if (this.indexOf(metric.metric_name) === -1) {
                        this.push(metric.metric_name);
                    }
                }, this);
            }, metrics);
            console.log("metrics = "+metrics.length);
            var resources = [];
            items.forEach(function(val) {
                val.metrics.forEach(function(metric) {
                    metric.resources.forEach(function(res) {
                        if (this.indexOf(res.res_id) === -1) {
                            this.push(res.res_id);
                        }
                    }, this);
                }, this);
            }, resources);
            console.log("resources = "+resources.length);
            var resource_types = [];
            items.forEach(function(val) {
                val.metrics.forEach(function(metric) {
                    metric.resources.forEach(function(res) {
                        if (this.indexOf(res.res_type) === -1) {
                            this.push(res.res_type);
                        }
                    }, this);
                }, this);
            }, resource_types);
            console.log("resource_types = "+resource_types.length);
            //var facets = emptyFacets.clone();
            $scope.$broadcast("facets_updated", emptyFacets);
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

