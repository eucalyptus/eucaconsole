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
        $scope.landingPageView = "tableview";
        $scope.urlParams = $.url().param();
        $scope.pageResource = '';
        $scope.sortByCookie = '';
        $scope.sortReverseCookie = '';
        $scope.landingPageViewCookie = '';
        $scope.initController = function (sortKey, jsonItemsEndpoint) {
            // TEMP SOl. to extrac the page resource string. After the merge of GUI-172, this part should be refactored
            var tempArray = jsonItemsEndpoint.split('/');
            tempArray.pop();
            var pageResource = tempArray.pop();

            $scope.initCookieStrings(pageResource);
            $scope.setInitialSort(sortKey);
            $scope.getItems(jsonItemsEndpoint);
            $scope.setWatch();
        };
        $scope.initCookieStrings = function (pageResource){
            $scope.pageResource = pageResource;
            $scope.sortByCookie = $scope.pageResource + "-sortBy";
            $scope.sortReverseCookie = $scope.pageResource + "-sortReverse";
            $scope.landingPageViewCookie = $scope.pageResource + "-landingPageView";
        };
        $scope.setInitialSort = function (sortKey) {
            if($.cookie($scope.sortByCookie) == null ){
                $scope.sortBy = sortKey;
            }else{
                $scope.sortBy = $.cookie($scope.sortByCookie);
            }

            if($.cookie($scope.sortReverseCookie) == null ){
                $scope.sortReverse = false;
            }else{
                $scope.sortReverse = ($.cookie($scope.sortReverseCookie) === 'true');
            }

            if($.cookie($scope.landingPageViewCookie) == null ){
                $scope.landingPageView = "tableview";
            }else{
                $scope.landingPageView = $.cookie($scope.landingPageViewCookie);
            }
        };
        $scope.setWatch = function () {
            var sortingDropdown = $('#sorting-dropdown'),
                sortingReverse = $('#sorting-reverse');
            $scope.$watch('sortBy',  function () {
                if (sortingDropdown.hasClass('open')) {
                    sortingDropdown.removeClass('open');
                    sortingDropdown.removeAttr('style');
                }
                // Set sortBy Cookie
                $.cookie($scope.sortByCookie, $scope.sortBy);
            });
            $scope.$watch('sortReverse', function(){
                if( $scope.sortReverse == true ){
                    sortingReverse.removeClass('down-caret');
                    sortingReverse.addClass('up-caret');
                }else{
                    sortingReverse.removeClass('up-caret');
                    sortingReverse.addClass('down-caret');
                }
                // Set SortReverse Cookie
                $.cookie($scope.sortReverseCookie, $scope.sortReverse);
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
               // Set landingPageView Cookie
               $.cookie($scope.landingPageViewCookie, $scope.landingPageView);
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
        $scope.switchView = function(view){
            $scope.landingPageView = view;
        };
    })
;
