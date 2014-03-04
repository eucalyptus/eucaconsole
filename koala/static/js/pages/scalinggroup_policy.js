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
            var modal = $scope.alarmModal;
            modal.foundation('reveal', 'open');
            setTimeout(function(){
                    var inputElement = modal.find('input[type!=hidden]').get(0);
                    if( inputElement != undefined ){
                        inputElement.focus()
                    }else{
                        modal.find('button').get(0).focus();
                    }
               }, 1000);
        };
    })
;

