/**
 * @fileOverview Scaling Group Create Policy page JS
 * @requires AngularJS
 *
 */

angular.module('ScalingGroupPolicy', [])
    .controller('ScalingGroupPolicyCtrl', function ($scope) {
        $scope.alarmModal = $('#create-alarm-modal');
        $scope.revealAlarmModal = function () {
            $scope.alarmModal.foundation('reveal', 'open');
        };
    })
;

