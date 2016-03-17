angular.module('ScalingGroupsServiceModule', [])
.factory('ScalingGroupsService', ['$http', '$interpolate', function ($http, $interpolate) {
    var getPolicyUrl = $interpolate('/scalinggroups/{{ id }}/policies/json');

    return {
        getScalingGroups: function () {
            var policyUrl = '/scalinggroups/json';
            return $http({
                method: 'GET',
                url: policyUrl
            }).then(function success (response) {
                var data = response.data || {
                    scalinggroups: []
                };
                return data.scalinggroups;
            }, function error (response) {
                return response;
            });
        },

        getPolicies: function (id) {
            var policyUrl = getPolicyUrl({id: id});
            return $http({
                method: 'GET',
                url: policyUrl
            }).then(function success (response) {
                var data = response.data || {
                    policies: {}
                };
                return data;
            }, function error (response) {
                return response;
            });
        }
    };
}]);
