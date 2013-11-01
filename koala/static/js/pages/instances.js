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
        $scope.searchFilterInstances = function() {
            // Filter instances client side based on search criteria.
            // Leverages Array.prototype.filter and Object.keys, EcmaScript 5 methods supported in recent browsers
            // TODO: Need to reset the instances array prior to performing subsequent filtering
            var filterText = $scope.searchFilter;
            var filteredInstances = $scope.instances.filter(function(item) {
                var keys = Object.keys(item);
                for (var i=0; i < keys.length; i++) {
                    var itemProp = item[keys[i]];
                    if (typeof itemProp === "string" && itemProp.indexOf(filterText) !== -1) {
                        return item;
                    }
                }
            });
            if (filterText) {
                $scope.instances = filteredInstances;
            } else {
                $scope.instances = $scope.getInstances();
            }
        };
    })
;
