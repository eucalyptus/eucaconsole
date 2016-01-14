angular.module('AlarmDetailPage', ['AlarmsComponents'])
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
