/**
 * @fileOverview Scaling Group History Page JS
 * @requires AngularJS
 *
 */

angular.module('ScalingGroupHistory', ['MagicSearch', 'EucaConsoleUtils'])
    .controller('ScalingGroupHistoryCtrl', function ($scope, $http, $timeout, eucaUnescapeJson, eucaHandleError) {
        $scope.historyLoading = true;
        $scope.resources = [];
        $scope.codeEditor = null;
        $scope.initPage = function (historyUrl) {
            $scope.scalinggroupHistoryUrl = historyUrl;
            if ($scope.scalinggroupHistoryUrl) {
                $scope.getScalinggroupHistory();
            }
        };
        $scope.revealModal = function (action, stack) {
            $scope.stackName = stack.name;
            var modal = $('#' + action + '-stack-modal');
            modal.foundation('reveal', 'open');
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
                    $scope.searchHistory();
                    $('#history-table').stickyTableHeaders();
                }
            });
        };
        $scope.searchHistory = function() {
            var filterText = ($scope.searchFilter || '').toLowerCase();
            if (filterText === '') {
                // If the search filter is empty, skip the filtering
                $scope.history = $scope.unfilteredHistory;
                return;
            }
            // Leverage Array.prototype.filter (ECMAScript 5)
            var filteredItems = $scope.unfilteredHistory.filter(function(item) {
                var filterKeys = ['status', 'type', 'physical_id', 'logical_id'];
                for (var i=0; i < filterKeys.length; i++) {  // Can't use $.each or Array.prototype.forEach here
                    var propName = filterKeys[i];
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
            $scope.scalinggroupHistoryUrl = decodeURIComponent($scope.scalinggroupHistoryUrl + "?" + query);
            $scope.getScalinggroupHistory();
        });
        $scope.$on('textSearch', function($event, text, filter_keys) {
            $scope.searchFilter = text;
            $timeout(function() {
                $scope.searchHistory();
            });
        });
    })
;

