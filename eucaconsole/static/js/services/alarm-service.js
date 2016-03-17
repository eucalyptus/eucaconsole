angular.module('AlarmServiceModule', [])
.factory('AlarmService', ['$http', function ($http) {
    return {
        updateAlarm: function (alarm, path, csrf_token, flash) {
            return $http({
                method: 'PUT',
                url: path,
                data: {
                    alarm: alarm,
                    csrf_token: csrf_token,
                    flash: flash
                }
            });
        },

        deleteAlarms: function (alarms, path, csrf_token, flash) {
            var alarmNames = alarms.map(function (current) {
                return current.name;
            });

            return $http({
                method: 'DELETE',
                url: path,
                data: {
                    alarms: alarmNames,
                    csrf_token: csrf_token,
                    flash: flash
                }
            });
        },

        updateActions: function (actions, path) {
            return $http({
                method: 'PUT',
                url: path,
                data: {
                    actions: actions
                }
            });
        }
    };
}]);
