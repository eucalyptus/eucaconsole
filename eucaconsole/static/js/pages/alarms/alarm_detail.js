angular.module('AlarmDetailPage', ['AlarmsComponents', 'EucaChosenModule'])
.directive('alarmDetail', function () {
    return {
        restrict: 'A',
        scope: {
        },
        link: function () {
            console.log('Alarm Detail!');
        },
        controller: function () {
        }
    };
});
