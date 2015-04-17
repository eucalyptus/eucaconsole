/**
 * @fileOverview Instance Monitoring page JS
 * @requires AngularJS
 *
 */

angular.module('InstanceMonitoring', ['CloudWatchCharts', 'EucaConsoleUtils'])
    .controller('InstanceMonitoringCtrl', function (eucaUnescapeJson) {
        var vm = this;
        vm.initController = initController;
        vm.submitMonitoringForm = submitMonitoringForm;
        vm.monitoringDuration = '3600';  // Default duration value is one hour
        vm.monitoringDurationChoices = [];

        function submitMonitoringForm() {
            document.getElementById('monitoring-form').submit();
        }

        function initController(optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            angular.forEach(options.monitoring_duration_choices, function(value, label) {
                vm.monitoringDurationChoices.push({val: value, label: label});
            });
        }
    })
;

