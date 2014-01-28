/**
 * @fileOverview Volumes landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('VolumesPage', ['CustomFilters'])
    .controller('VolumesCtrl', function ($scope) {
        $scope.volumeID = '';
        $scope.volumeZone = '';
        $scope.instancesByZone = '';
        $scope.urlParams = $.url().param();
        $scope.displayType = $scope.urlParams['display'] || 'tableview';
        $scope.initPage = function (instancesByZone) {
            $scope.instancesByZone = instancesByZone;
        };
        $scope.revealModal = function (action, volume) {
            var modal = $('#' + action + '-volume-modal'),
                volumeZone = volume['zone'];
            $scope.volumeID = volume['id'];
            if (action === 'attach') {
                // Set instance choices for attach to instance widget
                modal.on('open', function() {
                    var instanceSelect = $('#instance_id'),
                        instances = $scope.instancesByZone[volumeZone],
                        options = '';
                    if (instances === undefined) {
                        options = "<option value=''>No available instances in the same availability zone</option>";
                    }
                    else {
                      instances.forEach(function (instance) {
                          options += '<option value="' + instance['id'] + '">' + instance['name'] + '</option>';
                      });
                    }
                    instanceSelect.html(options);
                    instanceSelect.trigger('chosen:updated');
                    instanceSelect.chosen({'width': '75%', search_contains: true});
                });
            }
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
        $scope.pageResource = '';
        $scope.sortByCookie = '';
        $scope.sortReverseCookie = '';
        $scope.landingPageViewCookie = '';
        $scope.initController = function (sortKey, jsonItemsEndpoint) {
            $scope.jsonEndpoint = jsonItemsEndpoint;

            // TEMP SOl. to extrac the page resource string. After the merge of GUI-172, this part should be refactored
            tempArray = jsonItemsEndpoint.split('/');
            tempArray.pop();
            var pageResource = tempArray.pop();

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
            };
        };
        $scope.setWatch = function(){
            $scope.$watch('sortBy',  function () {
                if ($('#sorting-dropdown').hasClass('open')) {
                    $('#sorting-dropdown').removeClass('open');
                    $('#sorting-dropdown').removeAttr('style');
                }
                // Set sortBy Cookie
                $.cookie($scope.sortByCookie, $scope.sortBy);
            });
            $scope.$watch('sortReverse', function(){
                if( $scope.sortReverse == true ){
                    $('#sorting-reverse').removeClass('down-caret');
                    $('#sorting-reverse').addClass('up-caret');
                }else{
                    $('#sorting-reverse').removeClass('up-caret');
                    $('#sorting-reverse').addClass('down-caret');
                } 
                // Set SortReverse Cookie
                $.cookie($scope.sortReverseCookie, $scope.sortReverse);
            });
            $scope.$watch('landingPageView', function(){
               if( $scope.landingPageView == 'gridview' ){
                   $('#gridview-button').addClass("selected");
                   $('#tableview-button').removeClass("selected");
               }else{
                   $('#tableview-button').addClass("selected");
                   $('#gridview-button').removeClass("selected");
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
                // Auto-refresh volumes if any of them are in progress
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

