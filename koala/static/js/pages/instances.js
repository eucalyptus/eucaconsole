/**
 * @fileOverview Instances landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('InstancesPage', ['CustomFilters'])
    .controller('InstancesCtrl', function ($scope) {
        $scope.instanceID = '';
        $scope.revealModal = function (action, instance) {
            var modal = $('#' + action + '-instance-modal');
            $scope.instanceID = instance['id'];
            $scope.rootDevice = instance['root_device'];
            modal.foundation('reveal', 'open');
        };
    })
    .controller('ItemsCtrl', function ($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.items = [];
        $scope.unfilteredItems = [];
        $scope.sortBy = '';
        $scope.sortReverse = false;
        $scope.landingPageView = "tableview";
        $scope.jsonEndpoint = '';
        $scope.searchFilter = '';
        $scope.itemsLoading = true;
        $scope.initialLoading = true;
        $scope.pageResource = '';
        $scope.sortByCookie = '';
        $scope.sortReverseCookie = '';
        $scope.landingPageViewCookie = '';
        $scope.initController = function (pageResource, sortKey, jsonItemsEndpoint) {
            $scope.jsonEndpoint = jsonItemsEndpoint;
            $scope.initCookieStrings(pageResource);
            $scope.setInitialSort(sortKey);
            $scope.setWatch();
            $scope.getItems();
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
        $scope.getItems = function () {
            $http.get($scope.jsonEndpoint).success(function(oData) {
                var results = oData ? oData.results : [];
                var transitionalCount = 0;
                $scope.itemsLoading = false;
                $scope.items = results;
                $scope.unfilteredItems = results;
                $scope.items.forEach(function (item) {
                    if (item['transitional']) {
                        transitionalCount += 1;
                    }
                });
                // Auto-refresh instances if any of them are in progress
                if (transitionalCount > 0) {
                    $timeout(function() { $scope.getItems(); }, 5000);  // Poll every 5 seconds
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

