/**
 * @fileOverview Create Alarm JS
 * @requires AngularJS
 *
 */
angular.module('CreateAlarm', [])
    .controller('CreateAlarmCtrl', function ($scope) {
        $scope.dimension = '';
        $scope.alarmDialog = $('#create-alarm-modal');
        $scope.setInitialValues = function () {
            $scope.dimension = $('#dimension').find(':selected').val();
        };
        $scope.initController = function () {
            $scope.setInitialValues();
        }
        $scope.alarmDialog.on('opened', function() {
            $scope.setInitialValues();
        })
    })
;
