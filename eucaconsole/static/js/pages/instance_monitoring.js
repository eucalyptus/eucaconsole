/**
 * @fileOverview Instance Monitoring page JS
 * @requires AngularJS
 *
 */

angular.module('InstanceMonitoring', ['CloudWatchCharts', 'EucaConsoleUtils'])
    .controller('InstanceMonitoringCtrl', function ($scope, eucaUnescapeJson) {
        var vm = this;
        vm.duration = '3600';  // Default duration value is one hour
        vm.durationChoices = [];
        vm.initController = initController;
        vm.submitMonitoringForm = submitMonitoringForm;
        vm.refreshCharts = refreshCharts;

        function submitMonitoringForm() {
            document.getElementById('monitoring-form').submit();
        }

        function initController(optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            angular.forEach(options.monitoring_duration_choices, function(value, label) {
                vm.durationChoices.push({val: value, label: label});
            });
        }

        function refreshCharts() {
            // Broadcast message to CW charts directive controller to refresh
            $scope.$broadcast('cloudwatch:refreshCharts');
        }
    })
;

