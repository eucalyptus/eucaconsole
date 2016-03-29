/**
 * @fileOverview Common JS for Landing pages
 * @requires AngularJS, jQuery, and Purl jQuery URL parser plugin
 *
 */


angular.module('LandingPage', ['CustomFilters', 'ngSanitize', 'MagicSearch', 'Expando'])
    .config(function($locationProvider) {
        $locationProvider.html5Mode({enabled:true, requireBase:false, rewriteLinks:false });
    })
    .controller('ItemsCtrl', function ($scope, $http, $timeout, $sanitize, $location) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.items = [];
        $scope.itemsLoading = true;
        $scope.state = {'allSelected': false};
        $scope.runningSmartRefresh = false;
        $scope.facetItems = [];
        $scope.unfilteredItems = [];
        $scope.selectedItems = [];
        $scope.filterKeys = [];
        $scope.sortBy = '';
        $scope.landingPageView = "tableview";
        $scope.jsonEndpoint = '';
        $scope.searchFilter = '';
        $scope.pageResource = '';
        $scope.sortByKey = '';
        $scope.landingPageViewKey = '';
        $scope.openDropdownID = ''; 
        $scope.limitCount = 100;  // Beyond this number a "show ___ more" button will appear.
        $scope.displayCount = $scope.limitCount;
        $scope.transitionalRefresh = true;
        $scope.serverFilter = false;
        $scope.initController = function (pageResource, sortKey, jsonItemsEndpoint, cloud_type) {
            pageResource = pageResource || window.location.pathname.split('/')[0];
            $scope.jsonEndpoint = jsonItemsEndpoint;
            $scope.initLocalStorageKeys(pageResource);
            $scope.setInitialSort(sortKey);
            $scope.getItems();
            $scope.setWatch();
            $scope.setFocus();
            $scope.enableInfiniteScroll();
            $scope.storeRegion();
            $scope.cloudType = cloud_type;
            if (cloud_type !== undefined && cloud_type === "aws") {
                $scope.serverFilter = true;
            }
        };
        $scope.initLocalStorageKeys = function (pageResource){
            $scope.pageResource = pageResource;
            $scope.sortByKey = $scope.pageResource + "-sortBy";
            $scope.landingPageViewKey = $scope.pageResource + "-landingPageView";
        };
        $scope.setInitialSort = function (sortKey) {
            // This applies to saving initial sort for tile view
            // Table view sorting is persisted via angular-smart-table stPersist directive where configured
            var storedSort = Modernizr.sessionstorage && sessionStorage.getItem($scope.sortByKey),
                storedLandingPageView = Modernizr.localstorage && localStorage.getItem($scope.landingPageViewKey) || "tableview";
            $scope.sortBy = storedSort || sortKey;
            $scope.landingPageView = storedLandingPageView;
        };
        $scope.setWatch = function () {
            // Dismiss sorting dropdown on sort selection
            var sortingDropdown = $('#sorting-dropdown');
            $scope.$watch('sortBy',  function () {
                if (sortingDropdown.hasClass('open')) {
                    sortingDropdown.removeClass('open');
                    sortingDropdown.removeAttr('style');
                }
                // Set sortBy in sessionStorage
                if (Modernizr.sessionstorage) {
                    sessionStorage.setItem($scope.sortByKey, $scope.sortBy);
                }
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
               if (Modernizr.localstorage) {
                   localStorage.setItem($scope.landingPageViewKey, $scope.landingPageView);
               }
            });
            // When unfilteredItems[] is updated, run it through the filter and build items[]
            $scope.$watch('unfilteredItems', function() {
                $scope.searchFilterItems();
            }, true); 
        };
        $scope.setFocus = function () {
            $('#search-filter').focus();
            $(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
                var modal = $(this);
                var modalID = $(this).attr('id');
                if( modalID.match(/terminate/)  || modalID.match(/delete/) || 
                    modalID.match(/release/) || modalID.match(/reboot/) ){
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
            $(document).on('close.fndtn.reveal', '[data-reveal]', function () {
                var modal = $(this);
                modal.find('input[type="text"]').val('');
                modal.find('input[type="number"]').val('');
                modal.find('input:checked').attr('checked', false);
                modal.find('textarea').val('');
                modal.find('div.error').removeClass('error');
                var chosenSelect = modal.find('select');
                if (chosenSelect.length > 0 && chosenSelect.attr('multiple') === undefined) {
                    chosenSelect.prop('selectedIndex', 0);
                    chosenSelect.trigger("chosen:updated");
                }
            });
            $(document).on('closed.fndtn.reveal', '[data-reveal]', function () {
                $('#search-filter').focus();
            });
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
            });
        };
        $scope.storeRegion = function () {
            var regionKey = ($scope.cloudType == 'aws')?"aws-region":"euca-region";
            if ($('#region-dropdown').length > 0 && Modernizr.localstorage) {
                localStorage.setItem(
                    regionKey, $('#region-dropdown').children('li[data-selected="True"]').children('a').attr('id'));
            }
        };
        $scope.restoreSelectedItemsState = function () {
            // Avoid wiping out selected items and automatically closing More Actions menu during smart refresh
            // NOTE: Do not wrap this in a $scope.runningSmartRefresh check since that would prevent
            //       the selected items from being restored after the final smart refresh cycle
            var moreActionsBtn = $('#more-actions-btn');
            var dropdownOpen = moreActionsBtn.hasClass('open');
            var selectedItemIds = $scope.selectedItems.map(function (item) {
                return item.id || item.name;
            });
            $timeout(function () {
                angular.forEach($scope.items, function(item) {
                    var itemId = item.id || item.name;
                    if (selectedItemIds.indexOf(itemId) !== -1) {
                        item.selected = true;
                    }
                });
                if (dropdownOpen) {
                    $timeout(function () {
                        moreActionsBtn.click();
                    });
                }
            });
        };
        $scope.getItems = function (okToRefresh) {
            var csrf_token = $('#csrf_token').val();
            var data = "csrf_token="+csrf_token;
            $scope.detectOpenDropdown();
            $http({method:'POST', url:$scope.jsonEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                var transitionalCount = 0;
                $scope.itemsLoading = false;
                $scope.unfilteredItems = results;
                $scope.unfilteredItems.forEach(function (item) {
                    if (!!item.transitional) {
                        transitionalCount += 1;
                    }
                });
                // Auto-refresh items if any are in a transitional state
                if ($scope.transitionalRefresh && transitionalCount > 0) {
                    if (!$scope.runningSmartRefresh || okToRefresh !== undefined) {
                        $scope.runningSmartRefresh = true;
                        $timeout(function() { $scope.getItems(true); }, 5000);  // Poll every 5 seconds
                    }
                }
                else {
                    $scope.runningSmartRefresh = false;
                }
                // Emit 'itemsLoaded' signal when items[] is updated
                $timeout(function() {
                    $scope.$emit('itemsLoaded', $scope.items);
                    // and re-open any action menus
                    $scope.clickOpenDropdown();
                    $scope.restoreSelectedItemsState();
                    $(document).foundation('tab', 'reflow');
                });
                if ($scope.serverFilter === false) {
                    $scope.facetFilterItems();
                }
                else {
                    $scope.facetItems = $scope.unfilteredItems;
                }
            }).error(function (oData, status) {
                if (oData === undefined && status === 0) {  // likely interrupted request
                    return;
                }
                var errorMsg = oData.message || null;
                if (errorMsg) {
                    if (errorMsg.indexOf('permissions') > -1) {
                        Notify.failure(errorMsg);
                    }
                    else if (status === 403 || status === 400) {  // S3 token expiration responses return a 400
                        $('#timed-out-modal').foundation('reveal', 'open');
                    } else {
                        Notify.failure(errorMsg);
                    }
                }
                
            });
        };
        var matchByFacet = function(facet, val) {
            if (typeof val === 'string') {
                if ($.inArray(val, facet) > -1 ||
                    $.inArray(val.toLowerCase(), facet) > -1) {
                    return true;
                }
            }
            if (typeof val === 'object') {
                // if object, assume it has valid id or name attribute
                if ($.inArray(val.id, facet) > -1 ||
                    $.inArray(val.name, facet) > -1) {
                    return true;
                }
            }
        };
        var filterByFacet = function(item) {
            // handle special case of empty facet value, match all
            if (this.facet.indexOf("") > -1) {
                return true;
            }
            var val = item[this.key];
            if (val === undefined || val === null) {
                return true;
            }
            if (Array.isArray(val)) {
                for (var i=0; i<val.length; i++) {
                    return matchByFacet(this.facet, val[i]);
                }
            }
            else {
                return matchByFacet(this.facet, val);
            }
        };
        /*  Apply facet filtering
         *  to apply text filtering, call searchFilterItems instead
         */
        $scope.facetFilterItems = function() {
            var query;
            var url = window.location.href;
            if (url.indexOf("?") > -1) {
                query = url.split("?")[1];
            }
            if (query !== undefined && query.length !== 0) {
                // prepare facets by grouping
                var tmp = query.split('&').sort();
                var facets = {};
                angular.forEach(tmp, function(item) {
                    var facet = item.split('=');
                    if (this[facet[0]] === undefined) {
                        this[facet[0]] = [];
                    }
                    this[facet[0]].push(facet[1]);
                }, facets);
                var results = $scope.unfilteredItems;
                // filter results
                for (var key in facets) {
                    results = results.filter(filterByFacet, {'facet': facets[key], 'key':key});
                }
                $scope.facetItems = results;
            }
            else {
                $scope.facetItems = $scope.unfilteredItems.slice();
            }
            $scope.searchFilterItems();
        };
        /*  Filter items client side based on search criteria.
         */
        $scope.searchFilterItems = function() {
            var filterText = ($scope.searchFilter || '').toLowerCase();
            if (filterText === '') {
                // If the search filter is empty, skip the filtering
                $scope.items = $scope.facetItems;
                return;
            }
            // Leverage Array.prototype.filter (ECMAScript 5)
            var filteredItems = $scope.facetItems.filter(function(item) {
                for (var i=0; i < $scope.filterKeys.length; i++) {  // Can't use $.each or Array.prototype.forEach here
                    var propName = $scope.filterKeys[i];
                    var itemProp = item.hasOwnProperty(propName) && item[propName];
                    if (itemProp && typeof itemProp === "string" && 
                        itemProp.toLowerCase().indexOf(filterText) !== -1) {
                        return item;
                    } else if (itemProp && typeof itemProp === "object") {
                        // In case of mutiple values, create a flat string and perform search
                        var flatString = $scope.getItemNamesInFlatString(itemProp);
                        if (flatString.toLowerCase().indexOf(filterText) !== -1) {
                            return item;
                        }
                    }
                }
            });
            // Update the items[] with the filtered items
            $scope.items = filteredItems;
        };
        $scope.getItemNamesInFlatString = function(items) {
            var flatString = '';
            angular.forEach(items, function(x) {
                if (x.hasOwnProperty('name')) {
                    flatString += x.name + ' ';
                }
            });
            return flatString;
        };
        $scope.switchView = function(view){
            $scope.landingPageView = view;
        };
        $scope.showMore = function () {
            if ($scope.displayCount < $scope.items.length) {
                $scope.displayCount += $scope.limitCount;
            }
        };
        // listen for showMore to allow specialized screens to use this
        $scope.$on('showMore', function($event) {
            $timeout(function () { $scope.showMore(); }, 50);
        });
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
        $scope.clickOpenDropdown = function () {
            if ($scope.openDropdownID !== '') {
               $('#' + $scope.openDropdownID).click();
            }
        };
        $scope.detectOpenDropdown = function () {
            $scope.openDropdownID = ''; 
            $('.f-dropdown').each(function() {
                if ($(this).hasClass('open')) {
                    $scope.openDropdownID = $(this).prev('.dropdown').attr('id'); 
                }
            });
        };
        $scope.handleItemSelection = function() {
            // set all checkbox state based on state of items.selected
            var allItemsCheckbox = document.getElementById('select-all-items-tableview') ||
                document.getElementById('select-all-items-tileview');
            var checkedIems = $scope.items.filter(function (item) {
                return item.selected;
            });
            if (!checkedIems.length) {
                $scope.state.allSelected = false;
            }
            // Set indeterminate state on select-all checkbox when checked and at least one item is unselected
            allItemsCheckbox.indeterminate = !!($scope.state.allSelected && checkedIems.length < $scope.items.length);
            if (!$scope.state.allSelected && checkedIems.length === $scope.items.length) {
                $scope.state.allSelected = true;
            }
            $scope.selectedItems = checkedIems;
        };
        $scope.setAllState = function() {
            $timeout(function() {
                angular.forEach($scope.items, function(item) {
                    item.selected = $scope.state.allSelected;
                });
                if ($scope.state.allSelected) {
                    $scope.selectedItems = $scope.items;
                } else {
                    $scope.selectedItems = [];
                }
            });
        };
        $scope.$on('searchUpdated', function($event, query) {
            // update url
            var url = window.location.href;
            if (url.indexOf("?") > -1) {
                url = url.split("?")[0];
            }
            if (query.length > 0) {
                url = url + "?" + query;
            }
            $location.search(query);
            window.history.pushState(null, "", $location.absUrl());
            if ($scope.serverFilter === true) {
                url = $scope.jsonEndpoint;
                if (url.indexOf("?") > -1) {
                    url = url.split("?")[0];
                }
                if (query.length > 0) {
                    url = url + "?" + query;
                }
                $scope.jsonEndpoint = url;
                $scope.itemsLoading=true;
                $scope.getItems();
            }
            else {
                $scope.facetFilterItems();
            }
        });
        $scope.$on('textSearch', function($event, text, filter_keys) {
            $scope.searchFilter = text;
            $scope.filterKeys = filter_keys;
            $timeout(function() {
                $scope.searchFilterItems();
            });
        });
    }).directive('stPersist', function () {  // Save angular-smart-table sorting state on subsequent page loads
        return {
            require: '^stTable',
            link: function (scope, element, attr, ctrl) {
                var nameSpace = attr.stPersist;
                var defaultSortColumn;
                scope.$watch(function () {
                    return ctrl.tableState();
                }, function (newValue, oldValue) {
                    if (newValue !== oldValue) {
                        sessionStorage.setItem(nameSpace, JSON.stringify(newValue));
                    }
                }, true);
                //fetch the table state when the directive is loaded
                if (sessionStorage.getItem(nameSpace)) {
                    var savedState = JSON.parse(sessionStorage.getItem(nameSpace));
                    var tableState = ctrl.tableState();
                    angular.extend(tableState, savedState);
                    ctrl.pipe();
                }
            }
        };
    })
;
