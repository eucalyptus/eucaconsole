/**
 * @fileOverview Create Alarm JS
 * @requires AngularJS and jQuery
 *
 */
angular.module('CreateAlarm', [])
    .controller('CreateAlarmCtrl', function ($scope, $timeout) {
        $scope.alarmDialog = $('#create-alarm-modal');
        $scope.statisticField = $('#statistic');
        $scope.metricField = $('#metric');
        $scope.dimensionField = $('#dimension');
        $scope.metric = '';
        $scope.unitField = $('#unit');
        $scope.unitLabel = '';
        $scope.metricUnitMapping = {};
        $scope.setInitialValues = function () {
            $scope.metricField.val($scope.metricField.find('option[selected]').val());
            $scope.metricField.trigger('change');
        };
        $scope.initController = function (metricUnitMapping) {
            $scope.metricUnitMapping = JSON.parse(metricUnitMapping);
            $scope.alarmDialog.on('opened', function () {
                $scope.setInitialValues();
            });
        };
        $scope.updateMetricNamespace = function () {
            var selectedOptionLabel = $scope.metricField.find('option[value="' + $scope.metric + '"]').text();
            $scope.namespace = selectedOptionLabel.split(' - ')[0];
            $timeout(function () {
                $scope.setUnitChoice();
                $scope.dimensionField.trigger('change');
            }, 50);
        };
        $scope.setUnitChoice = function () {
            var unitChoice = $scope.metricUnitMapping[$scope.metric];
            $scope.unitLabel = unitChoice;
            $scope.unitField.val(unitChoice);
        };
    })
;
