/**
 * @fileOverview Create Alarm JS
 * @requires AngularJS
 *
 */
angular.module('CreateAlarm', [])
    .controller('CreateAlarmCtrl', function ($scope) {
        $scope.alarmDialog = $('#create-alarm-modal');
        $scope.metric = '';
        $scope.namespace = '';
        $scope.updateDimensionChoices = function () {
            var selectedOptionLabel = $('#metric').find('option[value="' + $scope.metric + '"]').text();
            $scope.namespace = selectedOptionLabel.split(' - ')[0];
        }
    })
;
