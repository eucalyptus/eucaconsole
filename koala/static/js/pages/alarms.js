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
        };
    })
;

