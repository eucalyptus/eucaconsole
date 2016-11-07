/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview factory method for instances XHR calls
 * @requires AngularJS
 *
 */
angular.module('InstancesServiceModule', [])
.factory('InstancesService', ['$http', function ($http) {
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    return {
        getInstances: function (csrfToken) {
            return $http({
                method: 'POST',
                url: '/instances/json',
                data: 'csrf_token=' + csrfToken,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }).then(function success (response) {
                var data = response.data || {
                    results: []
                };
                return data.results;
            });
        }
    };
}]);
