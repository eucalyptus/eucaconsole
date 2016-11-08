/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview factory methods for alarm XHR calls
 * @requires AngularJS, jQuery
 *
 */
angular.module('AlarmServiceModule', [])
.factory('AlarmService', ['$http', '$interpolate', function ($http, $interpolate) {
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

    return {
        getAlarm: function (id) {
            return $http({
                method: 'GET',
                url: '/alarms/' + btoa(id) + '/json'
            }).then( function (response) {
                return response.data || {
                    alarm: {}
                };
            });
        },

        createAlarm: function (alarm, csrf_token) {
            return $http({
                method: 'PUT',
                url: '/alarms',
                data: {
                    alarm: alarm,
                    csrf_token: csrf_token
                }
            });
        },

        updateAlarm: function (alarm, csrf_token, flash) {
            return $http({
                method: 'PUT',
                url: '/alarms',
                data: {
                    alarm: alarm,
                    csrf_token: csrf_token,
                    flash: flash
                }
            });
        },

        deleteAlarms: function (alarms, csrf_token, flash) {
            var alarmNames = alarms.map(function (current) {
                return current.name;
            });

            return $http({
                method: 'DELETE',
                url: '/alarms',
                data: {
                    alarms: alarmNames,
                    csrf_token: csrf_token,
                    flash: flash
                }
            });
        },

        getHistory: function (id) {
            return $http({
                method: 'GET',
                url: '/alarms/' + btoa(id) + '/history/json'
            }).then(function (response) {
                var data = response.data || {
                    history: []
                };
                return data.history;
            });
        },

        getAlarmsForResource: function (id, type) {
            return $http({
                method: 'GET',
                url: $interpolate('/alarms/resource/{{id}}/json')({id: id}),
                params: {
                    'resource-type': type
                }
            }).then(function success (response) {
                var data = response.data.results || [];
                return data;
            });
        },

        getAlarmNames: function (id, type) {
            return $http({
                method: 'GET',
                url: '/alarms/names/json'
            }).then(function success (response) {
                return response.data.results || [];
            });
        },

    };
}]);
