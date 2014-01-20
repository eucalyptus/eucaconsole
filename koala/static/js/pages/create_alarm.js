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
        $scope.unitField = $('#unit');
        $scope.setInitialValues = function () {
            $scope.metricField.val($scope.metricField.find('option[selected]').val());
            $scope.metricField.trigger('change');
        };
        $scope.initController = function () {
            $scope.alarmDialog.on('opened', function () {
                $scope.setInitialValues();
            });
        };
        $scope.updateMetricNamespace = function () {
            var selectedOptionLabel = $scope.metricField.find('option[value="' + $scope.metric + '"]').text();
            $scope.namespace = selectedOptionLabel.split(' - ')[0];
            $scope.setUnitChoice();
            $timeout(function () {
                $scope.dimensionField.trigger('change');
            }, 50);
        };
        $scope.setUnitChoice = function () {
            if ($scope.namespace = 'AWS/AutoScaling') {
                $scope.unitField.val('Count');
            }
        };
    })
;
