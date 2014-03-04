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
            var modal = $scope.createModal;
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
        $scope.revealDeleteModal = function (alarmName) {
            var modal = $scope.deleteModal;
            $scope.alarmName = alarmName;
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

