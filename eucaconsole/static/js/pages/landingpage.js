/**
 * @fileOverview Common JS for Landing pages
 * @requires AngularJS, jQuery, and Purl jQuery URL parser plugin
 *
 */


angular.module('LandingPage', ['CustomFilters', 'ngSanitize'])
    .controller('ItemsCtrl', function ($scope, $http, $timeout, $sanitize) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.items = [];
        $scope.itemsLoading = true;
        $scope.unfilteredItems = [];
        $scope.sortBy = '';
        $scope.landingPageView = "tableview";
        $scope.jsonEndpoint = '';
        $scope.searchFilter = '';
        $scope.pageResource = '';
        $scope.sortByKey = '';
        $scope.landingPageViewKey = '';
        $scope.limitCount = 100;  // Beyond this number a "show ___ more" button will appear.
        $scope.displayCount = $scope.limitCount;
        $scope.transitionalRefresh = true;
        $scope.initController = function (pageResource, sortKey, jsonItemsEndpoint) {
            $scope.initChosenFilters();
            pageResource = pageResource || window.location.pathname.split('/')[0];
            $scope.jsonEndpoint = jsonItemsEndpoint;
            $scope.initLocalStorageKeys(pageResource);
            $scope.setInitialSort(sortKey);
            $scope.getItems();
            $scope.setWatch();
            $scope.setFocus();
            $scope.setDropdownMenusListener();
            $scope.enableInfiniteScroll();
        };
        $scope.initChosenFilters = function () {
            !!$(document).chosen && $('#filters').find('select').chosen({
                'width': '100%', 'search_contains': true, 'placeholder_text_multiple': 'select...'
            });
        };
        $scope.initLocalStorageKeys = function (pageResource){
            $scope.pageResource = pageResource;
            $scope.sortByKey = $scope.pageResource + "-sortBy";
            $scope.landingPageViewKey = $scope.pageResource + "-landingPageView";
        };
        $scope.setInitialSort = function (sortKey) {
            var storedSort = sessionStorage.getItem($scope.sortByKey),
                storedLandingPageView = localStorage.getItem($scope.landingPageViewKey);
            $scope.sortBy = storedSort || sortKey;
            $scope.landingPageView = storedLandingPageView == null ? "tableview" : storedLandingPageView;
        };
        $scope.setWatch = function () {
            // Dismiss sorting dropdown on sort selection
            var sortingDropdown = $('#sorting-dropdown');
            $scope.$watch('sortBy',  function () {
                if (sortingDropdown.hasClass('open')) {
                    sortingDropdown.removeClass('open');
                    sortingDropdown.removeAttr('style');
                }
                // Set sortBy in localStorage
                sessionStorage.setItem($scope.sortByKey, $scope.sortBy);
            });
            // Landing page display preference (table/tile view) watcher
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
        $scope.setFocus = function () {
            $('#search-filter').focus();
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var modalID = $(this).attr('id');
                if( modalID.match(/terminate/)  || modalID.match(/delete/) || modalID.match(/release/) ){
                    var closeMark = modal.find('.close-reveal-modal');
                    if(!!closeMark){
                        closeMark.focus();
                    }
                }else{
                    var inputElement = modal.find('input[type!=hidden]').get(0);
                    var modalButton = modal.find('button').get(0);
                    if (!!inputElement) {
                        inputElement.focus();
                    } else if (!!modalButton) {
                        modalButton.focus();
                    }
               }
            });
            $(document).on('close', '[data-reveal]', function () {
                var modal = $(this);
                modal.find('input[type="text"]').val('');
                modal.find('input[type="number"]').val('');
                modal.find('input:checked').attr('checked', false);
                modal.find('textarea').val('');
                modal.find('div.error').removeClass('error');
                var chosenSelect = modal.find('select');
                if (chosenSelect.length > 0) {
                    chosenSelect.prop('selectedIndex', 0);
                    chosenSelect.trigger("chosen:updated");
                }
            });
            $(document).on('closed', '[data-reveal]', function () {
                $('#search-filter').focus();
            });
        };
        $scope.setDropdownMenusListener = function () {
            var modals = $('[data-reveal]');
            modals.on('open', function () {
                $('.gridwrapper').find('.f-dropdown').filter('.open').css('display', 'none');
            });
            modals.on('close', function () {
                $('.gridwrapper').find('.f-dropdown').filter('.open').css('display', 'block');
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
                    if (!!item['transitional']) {
                        transitionalCount += 1;
                    }
                });
                // Auto-refresh items if any are in a transitional state
                if ($scope.transitionalRefresh && transitionalCount > 0) {
                    $timeout(function() { $scope.getItems(); }, 5000);  // Poll every 5 seconds
                }
                $scope.$emit('itemsLoaded', $scope.items);
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
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
        $scope.switchView = function(view){
            $scope.landingPageView = view;
        };
        $scope.showMore = function () {
            if ($scope.displayCount < $scope.items.length) {
                $scope.displayCount += $scope.limitCount;
            }
        };
        $scope.enableInfiniteScroll = function () {
            $(window).scroll(function() {
                if ($(window).scrollTop() == $(document).height() - $(window).height()) {
                    $timeout(function () { $scope.showMore(); }, 50);
                }
            });
        };
        $scope.sanitizeContent = function (content) {
            return $sanitize(content);
        };
        // listen for refresh to allow other controllers to trigger this
        $scope.$on('refresh', function($event) {
            $scope.itemsLoading=true;
            $scope.getItems();
        });
    })
;
