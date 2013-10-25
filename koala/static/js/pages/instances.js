/**
 * @fileOverview Instances landing page
 * @requires AngularJS
 *
 */

angular.module('InstancesLandingPage', [])
    .config(function ($httpProvider) {
        $httpProvider.defaults.headers.common['X-CSRFToken'] = $.cookie('csrftoken');
    })
    .controller('InstancesCtrl', function ($scope, $http) {
        $scope.instances = [];
        $scope.getInstances = function() {
            var url = window.URLS.getInstancesJson;
            $scope.instancesLoading = true;
            $http.get(url).success(function(oData) {
                $scope.instancesLoading = false;
                $scope.instances = oData ? oData.results : [];
            });
        };
    })
;
