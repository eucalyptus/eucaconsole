/**
 * @fileOverview Create Alarm JS
 * @requires AngularJS and jQuery
 *
 */
angular.module('CreateAlarm', [])
    .controller('CreateAlarmCtrl', function ($scope, $timeout) {
        $scope.alarmDialog = $('#create-alarm-modal');
        $scope.updateMetricNamespace = function () {
            var selectedOptionLabel = $('#metric').find('option[value="' + $scope.metric + '"]').text();
            $scope.namespace = selectedOptionLabel.split(' - ')[0];
            $timeout(function () {
                $('#dimension').trigger('change');
            }, 50)
        };
    })
;
