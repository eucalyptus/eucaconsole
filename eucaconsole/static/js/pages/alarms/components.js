angular.module('AlarmsComponents', [])
.directive('alarmState', function () {
    var stateValues = {
        'OK': 'OK',
        'ALARM': 'Alarm',
        'INSUFFICIENT_DATA': 'Insufficient data'
    };
    var stateClasses = {
        'OK': 'success',
        'ALARM': 'alert',
        'INSUFFICIENT_DATA': 'secondary'
    };
    return {
        restrict: 'A',
        scope: {
            alarmState: '@'
        },
        template: '<span class="label status radius" ng-class="alarmClass()">{{ stateDisplay }}</span>',
        controller: function ($scope) {
            var alarmState = $scope.alarmState || 'INSUFFICIENT_DATA';
            $scope.stateDisplay = stateValues[alarmState];

            $scope.alarmClass = function () {
                return stateClasses[alarmState];
            };
        }
    };
});
