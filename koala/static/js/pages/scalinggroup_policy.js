/**
 * @fileOverview Scaling Group Create Policy page JS
 * @requires AngularJS
 *
 */

// Add Scaling Group Policy page includes the Create Alarm dialog, so pull in that module
angular.module('ScalingGroupPolicy', ['CreateAlarm'])
    .controller('ScalingGroupPolicyCtrl', function ($scope) {
        $scope.alarmModal = $('#create-alarm-modal');
        $scope.revealAlarmModal = function () {
            $scope.alarmModal.foundation('reveal', 'open');
        };
    })
;

