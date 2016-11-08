/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview factory method for VPC XHR calls
 * @requires AngularJS
 *
 */
angular.module('VPCServiceModule', [])
.factory('VPCService', ['$http', function ($http) {
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    return {
        getVPCNetworks: function () {
            return $http({
                method: 'GET',
                url: '/vpcnetworks/json'
            }).then(function success (response) {
                var data = response.data || {
                    results: []
                };
                return data.results;
            });
        },
        getVPCSubnets: function () {
            return $http({
                method: 'GET',
                url: '/vpcsubnets/json'
            }).then(function success (response) {
                var data = response.data || {
                    results: []
                };
                return data.results;
            });
        },
        getVPCSecurityGroups: function () {
            return $http({
                method: 'GET',
                url: '/vpcsecuritygroups/json'
            }).then(function success (response) {
                var data = response.data || {
                    results: []
                };
                return data.results;
            });
        }
    };
}]);
