/**
 * @fileOverview Create Alarm JS
 * @requires AngularJS and jQuery
 *
 */
angular.module('CreateAlarm', [])
    .controller('CreateAlarmCtrl', function ($scope, $timeout) {
        $scope.alarmDialog = $('#create-alarm-modal');
        $scope.unit = '';
        $scope.metric = '';
        $scope.setInitialValues = function () {
            $scope.statistic = $('#statistic').find(':selected').val();
            $scope.metric = $('#metric').find(':selected').val();
        };
        $scope.initController = function () {
            $scope.alarmDialog.on('opened', function () {
                $scope.setInitialValues();
            });
        };
        $scope.updateMetricNamespace = function () {
            var selectedOptionLabel = $('#metric').find('option[value="' + $scope.metric + '"]').text();
            $scope.namespace = selectedOptionLabel.split(' - ')[0];
            $timeout(function () {
                $('#dimension').trigger('change');
            }, 50);
            $scope.setUnitChoice();
        };
        $scope.setUnitChoice = function () {
            if ($scope.namespace = 'AWS/AutoScaling') {
                $scope.unit = 'Count';
            }
            $('#unit').trigger('change');
        };
    })
;
