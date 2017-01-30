/**
 * Copyright 2017 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Route target service module
 * @requires AngularJS
 *
 */
angular.module('RouteTargetServiceModule', [])
.factory('RouteTargetService', ['$http', '$interpolate', function ($http, $interpolate) {
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    return {
        getRouteTargets: function (vpcId) {
            return $http({
                method: 'GET',
                url: $interpolate('/vpcs/{{vpcId}}/route-targets-json')({vpcId: vpcId})
            }).then(function success (response) {
                var data = response.data || {
                    results: []
                };
                return data.results;
            });
        }
    };
}]);

