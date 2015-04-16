/**
 * @fileOverview Instance Monitoring page JS
 * @requires AngularJS
 *
 */

angular.module('InstanceMonitoring', ['CloudWatchCharts'])
    .controller('InstanceMonitoringCtrl', function () {
        var vm = this;
        vm.submitMonitoringForm = function () {
            document.getElementById('monitoring-form').submit();
        };
    })
;

