/**
 * @fileOverview CloudWatch Metrics landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('MetricsPage', ['LandingPage', 'CloudWatchCharts'])
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
    .controller('MetricsCtrl', function ($scope) {
        var vm = this;
        vm.ec2SubMetric = 'instance';
        vm.elbSubMetric = 'elb';
        vm.initPage = function() {
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
        }
    })
;

