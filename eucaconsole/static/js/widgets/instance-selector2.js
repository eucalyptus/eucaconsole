/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Instance Selector Directive JS
 * @requires AngularJS
 *
 */

angular.module('InstancesSelectorModule', ['MagicSearch'])
.directive('instanceSelector', [function() {
    return {
        restrict: 'E',
        scope: {
            instanceList: '=',
            instancesLoading: '@'
        },
        templateUrl: '/_template/elbs/instance-selector',
        controller: ['$scope', '$timeout', function ($scope, $timeout) {
            //$scope.instancesLoading = true;
            $scope.state = {'allSelected': false};
            $scope.setAllState = function() {
                $timeout(function() {
                    angular.forEach($scope.instanceList, function(item) {
                        item.selected = $scope.state.allSelected;
                    });
                    if ($scope.state.allSelected) {
                        $scope.selectedInstances = $scope.instanceList;
                    } else {
                        $scope.selectedInstances = [];
                    }
                });
            };
            $scope.handleItemSelection = function() {
                // set all checkbox state based on state of items.selected
                var allItemsCheckbox = document.getElementById('instance-all-checkbox');
                var checkedIems = $scope.instanceList.filter(function (item) {
                    return item.selected;
                });
                if (!checkedIems.length) {
                    $scope.state.allSelected = false;
                }
                // Set indeterminate state on select-all checkbox when checked and at least one item is unselected
                if (allItemsCheckbox) {
                    allItemsCheckbox.indeterminate = !!($scope.state.allSelected && checkedIems.length < $scope.instanceList.length);
                }
                if (!$scope.state.allSelected && checkedIems.length === $scope.instanceList.length) {
                    $scope.state.allSelected = true;
                }
                $scope.selectedInstances = checkedIems;
            };
            $scope.$on('searchUpdated', function ($event, query) {
                $scope.searchQueryURL = '';
                if (query.length > 0) {
                   $scope.searchQueryURL = query;
                }
            });
            $scope.$on('textSearch', function ($event, text, filterKeys) {
                $scope.searchFilter = text;
                $timeout(function () {
                    $scope.searchFilterItems(filterKeys);
                });
            });
            /*  Filter items client side based on search criteria.
             *  @param {array} filterProps Array of properties to filter items on
             */
            $scope.searchFilterItems = function(filterProps) {
                var filterText = ($scope.searchFilter || '').toLowerCase();
                if (filterProps !== '' && filterProps !== undefined){
                    // Store the filterProps input for later use as well
                    $scope.filterKeys = filterProps;
                }
                if (filterText === '') {
                    // If the search filter is empty, skip the filtering
                    $scope.filteredInstances = $scope.instanceList;
                    return;
                }
                // Leverage Array.prototype.filter (ECMAScript 5)
                var filteredItems = $scope.instanceList.filter(function(item) {
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
                $scope.filteredInstances = filteredItems;
            };
            $scope.filteredInstances = $scope.instanceList;
        }]
    };
}]);
