/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview factory method for instances XHR calls
 * @requires AngularJS
 *
 */
angular.module('InstancesServiceModule', [])
.factory('InstancesService', ['$http', '$httpParamSerializer', function ($http, $httpParamSerializer) {
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    return {
        getInstances: function (csrfToken, params) {
            // Pass params as an object (e.g. {'subnet_id': 'subnet-123456'} to filter by subnet)
            params = params || {};
            params.csrf_token = csrfToken;
            var data = $httpParamSerializer(params);
            return $http({
                method: 'POST',
                url: '/instances/json',
                data: data,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }).then(function success (response) {
                var data = response.data || {
                    results: []
                };
                return data.results;
            });
        },
        terminateInstances: function (csrfToken, params) {
            params = params || {};
            params.csrf_token = csrfToken;
            var data = $httpParamSerializer(params);
            return $http({
                method: 'POST',
                url: '/instances/terminate',
                data: data,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }).then(function success (response) {
                return response;
            });

        }
    };
}]);
