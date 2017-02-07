/**
 * Copyright 2017 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview factory methods for reporting XHR calls
 * @requires AngularJS 
 *
 */
angular.module('ReportingServiceModule', [])
.factory('ReportingService', ['$http', '$interpolate', function ($http, $interpolate) {
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
            var url = '/reporting-api/monthlyusage?year=' + year + '&month=' + month;
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
