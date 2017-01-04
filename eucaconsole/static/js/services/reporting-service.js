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
                url: '/reporting_api/preferences'
            }).then( function (response) {
                return response.data || {
                    enabled: false
                };
            });
        },

        setReportingPrefs: function (enabled, bucketName, tags, csrf_token) {
            return $http({
                method: 'PUT',
                url: '/reporting_api/preferences',
                data: $.param({
                    enabled: enabled,
                    bucketName: bucketName,
                    tags: tags,
                    csrf_token: csrf_token
                })
            });
        },
    };
}]);
