/**
 * @fileOverview Common JS for Landing pages
 * @requires AngularJS, jQuery, and Purl jQuery URL parser plugin
 *
 */


angular.module('LandingPage', ['CustomFilters'])
    .controller('ItemsCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.items = [];
        $scope.unfilteredItems = [];
        $scope.sortBy = '';
        $scope.sortReverse = false;
        $scope.urlParams = $.url().param();
        $scope.initController = function (sortKey, jsonItemsEndpoint) {
            $scope.setInitialSort(sortKey);
            $scope.getItems(jsonItemsEndpoint);
        };
        $scope.setInitialSort = function (sortKey) {
            $scope.sortBy = sortKey;
            $scope.$watch('sortBy',  function () {
                if ($('#sorting-dropdown').hasClass('open')) {
                    $('#sorting-dropdown').removeClass('open');
                    $('#sorting-dropdown').removeAttr('style');
                }
            });
            $scope.$watch('sortReverse', function(){
                if( $scope.sortReverse == true ){
                    $('#sorting-reverse').removeClass('down-caret');
                    $('#sorting-reverse').addClass('up-caret');
                }else{
                    $('#sorting-reverse').removeClass('up-caret');
                    $('#sorting-reverse').addClass('down-caret');
                } 
            });
        };
        $scope.applyGetRequestFilters = function () {
            // Apply an "all" match of filters based on URL params
            // If item matches all applicable non-empty URL param filters, return the item.
            $scope.items = $scope.items.filter(function(item) {
                var urlParams = $scope.urlParams,
                    matchedKeys = [];
                delete urlParams['filter'];  // Ignore filter
                delete urlParams['display'];  // Ignore display = tableview | gridview
                var urlParamKeys = Object.keys(urlParams);
                var filteredKeys = [];
                for (var i=0; i < urlParamKeys.length; i++) {
                    if (urlParams[urlParamKeys[i]]) {
                        filteredKeys.push(1);  // Ignore empty URL params
                    }
                    if (item[urlParamKeys[i]] === urlParams[urlParamKeys[i]]) {
                        matchedKeys.push(1)
                    }
                }
                // If all URL param keys match, return item.
                if (matchedKeys.length === filteredKeys.length) {
                    return item;
                }
            });
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
        $scope.reverseSort = function(){
           $scope.sortReverse = !$scope.sortReverse
        };
    })
;
