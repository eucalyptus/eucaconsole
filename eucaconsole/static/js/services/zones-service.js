/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview factory method for availability zones XHR calls
 * @requires AngularJS
 *
 */
angular.module('ZonesServiceModule', [])
.factory('ZonesService', ['$http', function ($http) {
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    return {
        getZones: function () {
            return $http({
                method: 'GET',
                url: '/zones/json'
            }).then(function success (response) {
                var data = response.data || {
                    results: []
                };
                return data.results;
            });
        }
    };
}]);
