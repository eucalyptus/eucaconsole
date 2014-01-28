/**
 * @fileOverview JS for Scaling Groups landing page
 * @requires AngularJS and jQuery
 *
 */

angular.module('ScalingGroupsPage', ['CustomFilters'])
    .controller('ItemsCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.items = [];
        $scope.itemsLoading = true;
        $scope.unfilteredItems = [];
        $scope.sortBy = '';
        $scope.urlParams = $.url().param();
        $scope.initController = function (pageResource, sortKey, jsonItemsEndpoint) {
            $scope.initLocalStorageKeys(pageResource);
            $scope.setInitialSort(sortKey);
            $scope.getItems(jsonItemsEndpoint);
            $scope.setWatch();
        };
        $scope.setInitialSort = function (sortKey) {
            var storedSort = localStorage.getItem($scope.sortByKey),
                storedSortReverse = localStorage.getItem($scope.sortReverseKey),
                storedLandingPageView = localStorage.getItem($scope.landingPageViewKey);
            $scope.sortBy = storedSort || sortKey;
            $scope.sortReverse = storedSortReverse == null ? false : (storedSortReverse === 'true');
            $scope.landingPageView = storedLandingPageView == null ? "tableview" : storedLandingPageView;
        };
        $scope.setWatch = function () {
            var sortingDropdown = $('#sorting-dropdown'),
                sortingReverse = $('#sorting-reverse');
            $scope.$watch('sortBy',  function () {
                if (sortingDropdown.hasClass('open')) {
                    sortingDropdown.removeClass('open');
                    sortingDropdown.removeAttr('style');
                }
                // Set sortBy in localStorage
                localStorage.setItem($scope.sortByKey, $scope.sortBy);
            });
            $scope.$watch('sortReverse', function(){
                if ($scope.sortReverse == true) {
                    sortingReverse.removeClass('down-caret');
                    sortingReverse.addClass('up-caret');
                } else {
                    sortingReverse.removeClass('up-caret');
                    sortingReverse.addClass('down-caret');
                }
                // Set SortReverse in localStorage
                localStorage.setItem($scope.sortReverseKey, $scope.sortReverse);
            });
            $scope.$watch('landingPageView', function () {
                var gridviewBtn = $('#gridview-button'),
                    tableviewBtn = $('#tableview-button');
               if ($scope.landingPageView == 'gridview') {
                   gridviewBtn.addClass("selected");
                   tableviewBtn.removeClass("selected");
               } else {
                   tableviewBtn.addClass("selected");
                   gridviewBtn.removeClass("selected");
               }
               // Set landingPageView in localStorage
               localStorage.setItem($scope.landingPageViewKey, $scope.landingPageView);
            });
        };
        $scope.getItems = function (jsonItemsEndpoint) {
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
