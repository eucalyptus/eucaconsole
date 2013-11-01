/**
 * @fileOverview Instances landing page
 * @requires AngularJS
 *
 */

angular.module('InstancesLandingPage', [])
    .controller('InstancesCtrl', function ($scope, $http) {
        $scope.instances = [];
        $scope.unfilteredInstances = [];
        $scope.sortBy = '-created_date';
        $scope.getInstances = function() {
            var url = window.URLS.getInstancesJson;
            $scope.instancesLoading = true;
            $http.get(url).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.instancesLoading = false;
                $scope.instances = results;
                $scope.unfilteredInstances = results;
            });
        };
        $scope.searchFilterInstances = function() {
            // Filter instances client side based on search criteria.
            $scope.instances = $scope.unfilteredInstances;  // reset prior to applying filter
            var filterText = $scope.searchFilter;
            var filterProps = [
                "status", "instance_name", "instance_type", "availability_zone",
                "security_group", "instance_id", "created_date"
            ];
            // Leverage Array.prototype.filter (ECMAScript 5)
            var filteredInstances = $scope.instances.filter(function(item) {
                for (var i=0; i < filterProps.length; i++) {
                    var itemProp = item[filterProps[i]];
                    if (itemProp.indexOf(filterText) !== -1) {
                        return item;
                    }
                }
            });
            $scope.instances = filterText ? filteredInstances : $scope.unfilteredInstances;
        };
    })
;
