/**
 * @fileOverview Scaling Group History Page JS
 * @requires AngularJS
 *
 */

angular.module('ScalingGroupHistory', ['MagicSearch', 'EucaConsoleUtils', 'Expando'])
    .controller('ScalingGroupHistoryCtrl', function ($scope, $http, $timeout, eucaUnescapeJson, eucaHandleError) {
        $scope.historyLoading = true;
        $scope.facetHistory = [];
        $scope.unfilteredHistory = [];
        $scope.initPage = function (historyUrl, historyActivityUrl, sortKey) {
            $scope.scalinggroupHistoryUrl = historyUrl;
            $scope.scalinggroupHistoryActivityUrl = historyActivityUrl;
            $scope.sortByKey = "scalinghistory-sortBy";
            $scope.setInitialSort(sortKey);
            if ($scope.scalinggroupHistoryUrl) {
                $scope.getScalinggroupHistory();
            }
            $scope.$watch('sortBy',  function () {
                // Set sortBy in sessionStorage
                if (Modernizr.sessionstorage) {
                    sessionStorage.setItem($scope.sortByKey, $scope.sortBy);
                }
            });
        };
        $scope.setInitialSort = function (sortKey) {
            var storedSort = Modernizr.sessionstorage && sessionStorage.getItem($scope.sortByKey);
            $scope.sortBy = storedSort || sortKey;
        };
        $scope.toggleTab = function (tab) {
            $(".tabs").children("dd").each(function() {
                var id = $(this).find("a").attr("href").substring(1);
                var $container = $("#" + id);
                $(this).removeClass("active");
                $container.removeClass("active");
                if (id == tab || $container.find("#" + tab).length) {
                    $(this).addClass("active");
                    $container.addClass("active");
                    $scope.currentTab = id; // Update the currentTab value for the help display
                    $scope.$broadcast('updatedTab', $scope.currentTab);
                }
             });
        };
        $scope.clickTab = function ($event, tab){
            $event.preventDefault();
            // If there exists unsaved changes, open the wanring modal instead
            if ($scope.isNotChanged === false) {
                $scope.openModalById('unsaved-changes-warning-modal');
                $scope.unsavedChangesWarningModalLeaveCallback = function() {
                    $scope.isNotChanged = true;
                    $scope.toggleTab(tab);
                    $('#unsaved-changes-warning-modal').foundation('reveal', 'close');
                };
                return;
            } 
            $scope.toggleTab(tab);
        };
        $scope.getScalinggroupHistory = function () {
            //$scope.historyLoading = true;
            $http.get($scope.scalinggroupHistoryUrl).success(function(oData) {
                var results = oData ? oData.results : '';
                $scope.historyLoading = false;
                if (results) {
                    $scope.unfilteredHistory = results;
                    $scope.facetFilterHistory();
                    $('#history-table').stickyTableHeaders();
                }
            });
        };
        /*  Apply facet filtering
         *  to apply text filtering, call searchHistory instead
         */
        $scope.facetFilterHistory = function() {
            var query;
            var url = window.location.href;
            if (url.indexOf("?") > -1) {
                query = url.split("?")[1];
            }
            if (query !== undefined && query.length !== 0) {
                // prepare facets by grouping
                var tmp = query.split('&').sort();
                var facets = {};
                for (var i=0; i<tmp.length; i++) {
                    var facet = tmp[i].split('=');
                    if (facets[facet[0]] === undefined) {
                        facets[facet[0]] = [];
                    }
                    facets[facet[0]].push(facet[1]);
                }
                var results = $scope.unfilteredHistory;
                var filterFunc = function(item) {
                    var val = item.hasOwnProperty(key) && item[key];
                    if (typeof val === 'string' && $.inArray(val.toLowerCase(), facets[key]) > -1) {
                        return true;
                    }
                };
                for (var key in facets) {
                    results = results.filter(filterFunc);
                }
                $scope.facetHistory = results;
            }
            else {
                $scope.facetHistory = $scope.unfilteredHistory.slice();
            }
            $scope.searchHistory();
        };
        $scope.searchHistory = function() {
            var filterText = ($scope.searchFilter || '').toLowerCase();
            if (filterText === '') {
                // If the search filter is empty, skip the filtering
                $scope.history = $scope.facetHistory;
                return;
            }
            // Leverage Array.prototype.filter (ECMAScript 5)
            var filteredItems = $scope.facetHistory.filter(function(item) {
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
            $scope.history = filteredItems;
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
            window.history.pushState(query, "", url);
            $scope.facetFilterHistory();
        });
        $scope.$on('textSearch', function($event, text, filter_keys) {
            $scope.searchFilter = text;
            $scope.filterKeys = filter_keys;
            $timeout(function() {
                $scope.searchHistory();
            });
        });
    })
;

