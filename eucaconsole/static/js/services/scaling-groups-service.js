angular.module('ScalingGroupsServiceModule', [])
.factory('ScalingGroupsService', ['$http', '$interpolate', function ($http, $interpolate) {
    var getPolicyUrl = $interpolate('/scalinggroups/{{ id }}/policies/json');
    return {
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
