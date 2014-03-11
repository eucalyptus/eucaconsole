/**
 * @fileOverview Scaling Group Create Policy page JS
 * @requires AngularJS
 *
 */

// Add Scaling Group Policy page includes the Create Alarm dialog, so pull in that module
angular.module('ScalingGroupPolicy', ['CreateAlarm'])
    .controller('ScalingGroupPolicyCtrl', function ($scope) {
        $scope.alarmModal = $('#create-alarm-modal');
        $scope.initPage = function (){
            $scope.setFocus();
        };
        $scope.revealAlarmModal = function () {
            var modal = $scope.alarmModal;
            modal.foundation('reveal', 'open');
        };
        $scope.setFocus = function () {
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var inputElement = modal.find('input[type!=hidden]').get(0);
                var modalButton = modal.find('button').get(0);
                if (!!inputElement) {
                    inputElement.focus();
                } else if (!!modalButton) {
                    modalButton.focus();
                }
            });
        };
    })
;

