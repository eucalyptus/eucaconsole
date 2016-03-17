angular.module('ScalingGroupsServiceModule', ['EucaRoutes'])
.factory('ScalingGroupsService', ['$http', 'eucaRoutes', function ($http, eucaRoutes) {
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
                }, function error (response) {
                    return response;
                });
            });
        },

        getPolicies: function (id) {
            return eucaRoutes.getRouteDeferred('scalinggroup_policies_json', { id: id }).then(function (path) {
                return $http({
                    method: 'GET',
                    url: path
                }).then(function success (response) {
                    var data = response.data || {
                        policies: {}
                    };
                    return data;
                }, function error (response) {
                    return response;
                });
            });
        }
    };
}]);
