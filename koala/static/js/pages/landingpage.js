/**
 * @fileOverview Common JS for Landing pages
 * @requires AngularJS, jQuery, and Purl jQuery URL parser plugin
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
                    $scope.applyAnyGetRequestFilters();
                }
            });
        };
        /*  Filter items client side based on search criteria.
         *  @param {array} filterProps Array of properties to filter items on
         *  Note: We could potentially use Angular's template filter here, but it may be tricky to
         *        filter by nested properties (read: tags).
         */
        $scope.searchFilterItems = function(filterProps) {
            $scope.items = $scope.unfilteredItems;  // reset prior to applying filter
            var filterText = $scope.searchFilter || '';
            // Leverage Array.prototype.filter (ECMAScript 5)
            var filteredItems = $scope.items.filter(function(item) {
                for (var i=0; i < filterProps.length; i++) {  // Can't use $.each or Array.prototype.forEach here
                    var propName = filterProps[i];
                    var itemProp = item.hasOwnProperty(propName) && item[propName];
                    if (itemProp && itemProp.indexOf(filterText) !== -1) {
                        return item;
                    }
                    // Match array of objects (i.e. tags)
                    if (itemProp && $.type(itemProp === "array") && propName === "tags") {
                        for (var j=0; j < itemProp.length; j++) {  // Can't use $.each or Array.prototype.forEach here
                            if (itemProp[j]['key'].indexOf(filterText) !== -1 || itemProp[j]['value'].indexOf(filterText) !== -1) {
                                return item;
                            }
                        }
                    }
                }
            });
            $scope.items = filterText ? filteredItems : $scope.unfilteredItems;
        };
    })
;
