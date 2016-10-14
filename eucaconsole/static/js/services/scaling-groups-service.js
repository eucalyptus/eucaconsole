/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview factory method for scaling group XHR calls
 * @requires AngularJS, jQuery
 *
 */
angular.module('ScalingGroupsServiceModule', [])
.factory('ScalingGroupsService', ['$http', '$q', function ($http, $q) {
    return {
        getScalingGroups: function () {
            return $http({
                method: 'GET',
                url: '/scalinggroup/names/json'
            }).then(function success (response) {
                var data = response.data || {
                    scalinggroups: []
                };
                return data.scalinggroups;
            });
        },

        getPolicies: function (id) {
            if(!id) {
                return $q(function (resolve, reject) {
                    reject('No id passed.');
                });
            }
            return $http({
                method: 'GET',
                url: '/scalinggroup/' + id + '/policies/json'
            }).then(function success (response) {
                var data = response.data || {
                    policies: {}
                };
                return data;
            });
        }
    };
}]);
