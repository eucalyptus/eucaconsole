angular.module('AlarmServiceModule', ['EucaRoutes'])
.factory('AlarmService', ['$http', 'eucaRoutes', function ($http, eucaRoutes) {
    return {
        createAlarm: function (alarm, csrf_token) {
            return eucaRoutes.getRouteDeferred('cloudwatch_alarms').then(function (path) {
                return $http({
                    method: 'PUT',
                    url: path,
                    data: {
                        alarm: alarm,
                        csrf_token: csrf_token
                    }
                });
            });
        },

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
        }
    };
}]);
