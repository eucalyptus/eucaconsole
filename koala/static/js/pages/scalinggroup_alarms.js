/**
 * @fileOverview Scaling Group Alarms page JS
 * @requires AngularJS
 *
 */

angular.module('ScalingGroupAlarms', [])
    .controller('ScalingGroupAlarmsCtrl', function ($scope) {
        $scope.alarmName = '';
        $scope.createModal = $('#create-alarm-modal');
        $scope.deleteModal = $('#delete-alarm-modal');
        $scope.revealCreateModal = function () {
            $scope.createModal.foundation('reveal', 'open');
        };
        $scope.revealDeleteModal = function (alarmName) {
            $scope.alarmName = alarmName;
            $scope.deleteModal.foundation('reveal', 'open');
        };
    })
;

