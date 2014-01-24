/**
 * @fileOverview JS for Scaling Groups landing page
 * @requires AngularJS and jQuery
 *
 */

angular.module('ScalingGroupsPage', ['CustomFilters'])
    .controller('ItemsCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.items = [];
        $scope.unfilteredItems = [];
        $scope.sortBy = '';
        $scope.urlParams = $.url().param();
        $scope.initController = function (sortKey, jsonItemsEndpoint) {
            $scope.setInitialSort(sortKey);
            $scope.getItems(jsonItemsEndpoint);
        };
        $scope.setInitialSort = function (sortKey) {
            $scope.sortBy = sortKey;
        };
        $scope.getItems = function (jsonItemsEndpoint) {
            $scope.itemsLoading = true;
            $http.get(jsonItemsEndpoint).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = false;
                $scope.items = results;
                $scope.unfilteredItems = results;
                if ($.url().param('filter')) {
                    $scope.applyGetRequestFilters();
                }
            }).error(function (oData, status) {
                var errorMsg = oData['error'] || null;
                if (errorMsg && status === 403) {
                    alert(errorMsg);
                    $('#euca-logout-form').submit();
                }
            });
        };
        /*  Filter items client side based on search criteria.
         *  @param {array} filterProps Array of properties to filter items on
         */
        $scope.searchFilterItems = function(filterProps) {
            $scope.items = $scope.unfilteredItems;  // reset prior to applying filter
            var filterText = ($scope.searchFilter || '').toLowerCase();
            // Leverage Array.prototype.filter (ECMAScript 5)
            var filteredItems = $scope.items.filter(function(item) {
                for (var i=0; i < filterProps.length; i++) {  // Can't use $.each or Array.prototype.forEach here
                    var propName = filterProps[i];
                    var itemProp = item.hasOwnProperty(propName) && item[propName];
                    if (itemProp && typeof itemProp === "string" && itemProp.toLowerCase().indexOf(filterText) !== -1) {
                        return item;
                    }
                }
            });
            $scope.items = filterText ? filteredItems : $scope.unfilteredItems;
        };
    })
;
