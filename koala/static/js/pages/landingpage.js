/**
 * @fileOverview Common JS for Landing pages
 * @requires AngularJS and Purl jQuery URL parser
 *
 */

angular.module('LandingPage', [])
    .controller('ItemsCtrl', function ($scope, $http) {
        $scope.items = [];
        $scope.unfilteredItems = [];
        $scope.sortBy = '';
        $scope.urlParams = $.url().param();
        $scope.setInitialSort = function(sortKey) {
            $scope.sortBy = sortKey;
        };
        $scope.applyAnyGetRequestFilters = function() {
            $scope.items = $scope.items.filter(function(item) {
                for (var key in $scope.urlParams) {
                    if ($scope.urlParams.hasOwnProperty(key) && $.url().param(key)) {
                        console.log(key + ': ' + $.url().param(key));
                        if (item[key] === $.url().param(key)) {
                            return item
                        }
                    }
                }
            });
        };
        $scope.getItems = function(jsonItemsEndpoint) {
            $scope.itemsLoading = true;
            $http.get(jsonItemsEndpoint).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = false;
                $scope.items = results;
                $scope.unfilteredItems = results;
                if ($.url().param('filter')) {
                    if ($.url().param('anyall') === 'any') {
                        $scope.applyAnyGetRequestFilters();
                    }
                }
            });
        };
        /*  Filter items client side based on search criteria.
         *  @param {array} filterProps Array of properties to filter items on
         */
        $scope.searchFilterItems = function(filterProps) {
            $scope.items = $scope.unfilteredItems;  // reset prior to applying filter
            var filterText = $scope.searchFilter || '';
            // Leverage Array.prototype.filter (ECMAScript 5)
            var filteredItems = $scope.items.filter(function(item) {
                for (var i=0; i < filterProps.length; i++) {
                    var itemProp = item.hasOwnProperty(filterProps[i]) && item[filterProps[i]];
                    if (itemProp && itemProp.indexOf(filterText) !== -1) {
                        return item;
                    }
                }
            });
            $scope.items = filterText ? filteredItems : $scope.unfilteredItems;
        };
    })
;
