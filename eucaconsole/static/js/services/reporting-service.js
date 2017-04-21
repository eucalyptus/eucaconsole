/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview factory methods for reporting XHR calls
 * @requires AngularJS 
 *
 */
angular.module('ReportingServiceModule', [])
.factory('ReportingService', ['$http', '$httpParamSerializer', function ($http, $httpParamSerializer) {
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

    return {
        getReportingPrefs: function () {
            return $http({
                method: 'GET',
                url: '/reporting-api/preferences'
            }).then( function (response) {
                return response.data || {
                    enabled: false
                };
            });
        },

        setReportingPrefs: function (enabled, bucketName, tags, userReportsEnabled, csrf_token) {
            return $http({
                method: 'PUT',
                url: '/reporting-api/preferences',
                data: {
                    enabled: enabled,
                    bucketName: bucketName,
                    tags: tags,
                    userReportsEnabled: userReportsEnabled,
                    csrf_token: csrf_token
                }
            }).then( function (response) {
                return response.data || {};
            });
        },

        getMonthlyUsage: function (year, month) {
            var params = {year:year, month:month};
            return $http({
                method: 'GET',
                url: '/reporting-api/monthlyusage?' + $httpParamSerializer(params)
            }).then( function (response) {
                return response.data || {
                    enabled: false
                };
            });
        },

        getInstanceUsage: function (granularity, timePeriod, fromDate, toDate, groupBy, filters) {
            var params = {
                'granularity': granularity,
                'timePeriod': timePeriod,
                'fromTime': fromDate,
                'toTime': toDate,
                'groupBy': groupBy,
                'filters': JSON.stringify(filters)
            };
            return $http({
                method: 'GET',
                url: '/reporting-api/instanceusage?' + $httpParamSerializer(params)
            }).then( function (response) {
                return response.data || {
                    enabled: false
                };
            });
        },

        getMonthToDateUsage: function (year, month) {
            var url = '/reporting-api/monthtodateusage?year=' + year + '&month=' + month;
            return $http({
                method: 'GET',
                url: url
            }).then( function (response) {
                return response.data || {
                    enabled: false
                };
            });
        },

        getInstanceUsage: function (granularity, timePeriod, fromDate, toDate, groupBy) {
            var params = {
                'granularity': granularity,
                'timePeriod': timePeriod,
                'fromTime': fromDate,
                'toTime': toDate,
                'groupBy': groupBy
            };
            var url = '/reporting-api/instanceusage?' + $httpParamSerializer(params);
            return $http({
                method: 'GET',
                url: url
            }).then( function (response) {
                return response.data || {
                    enabled: false
                };
            });
        },
    };
}]);
