/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview factory method for scaling group XHR calls
 * @requires AngularJS, jQuery
 *
 */
angular.module('ScalingGroupsServiceModule', ['EucaRoutes'])
.factory('ScalingGroupsService', ['$http', '$q', 'eucaRoutes', function ($http, $q, eucaRoutes) {
    return {
        getScalingGroups: function () {
            return eucaRoutes.getRouteDeferred('scalinggroup_names_json').then(function (path) {
                return $http({
                    method: 'GET',
                    url: path
                }).then(function success (response) {
                    var data = response.data || {
                        scalinggroups: []
                    };
                    return data.scalinggroups;
                });
            });
        },

        getPolicies: function (id) {
            if(!id) {
                return $q(function (resolve, reject) {
                    reject('No id passed.');
                });
            }
            return eucaRoutes.getRouteDeferred('scalinggroup_policies_json', { id: id }).then(function (path) {
                return $http({
                    method: 'GET',
                    url: path
                }).then(function success (response) {
                    var data = response.data || {
                        policies: {}
                    };
                    return data;
                });
            });
        }
    };
}]);
