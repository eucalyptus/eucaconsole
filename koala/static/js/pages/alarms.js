/**
 * @fileOverview CloudWatch Alarms landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('AlarmsPage', ['LandingPage'])
    .controller('AlarmsCtrl', function ($scope) {
        $scope.alarmID = '';
        $scope.revealModal = function (action, item) {
            var modal = $('#' + action + '-alarm-modal');
            $scope.alarmID = item['id'];
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

