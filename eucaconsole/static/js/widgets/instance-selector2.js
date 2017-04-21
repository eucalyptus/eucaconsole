/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview Instance Selector Directive JS
 * @requires AngularJS
 *
 */

angular.module('InstancesSelectorModule', ['MagicSearch', 'MagicSearchFilterModule'])
.factory('InstancesFiltersService', ['$http', function ($http) {
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    return {
        getInstancesFilters: function () {
            return $http({
                method: 'GET',
                url: '/elbs/instances/filters'
            }).then(function success (response) {
                var data = response.data || {
                    results: []
                };
                return data.results;
            });
        }
    };
}])
.directive('instanceSelector', [function() {
    return {
        restrict: 'E',
        scope: {
            instanceList: '=',
            instancesLoading: '@'
        },
        templateUrl: '/_template/elbs/instance-selector',
        controller: ['$scope', '$timeout', 'InstancesFiltersService', 'MagicSearchFilterService', 'eucaHandleError',
        function ($scope, $timeout, InstancesFiltersService, MagicSearchFilterService, eucaHandleError) {
            InstancesFiltersService.getInstancesFilters().then(
                function success(result) {
                    $scope.facets = result;
                },
                function error(errData) {
                    eucaHandleError(errData.data.message, errData.status);
                    vm.instancesLoading = false;
                });
            $scope.facets = '[]';
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
                $scope.facetFilterItems(query);
            });
            $scope.$on('textSearch', function ($event, text, filterKeys) {
                $scope.searchFilter = text;
                $timeout(function () {
                    $scope.searchFilterItems(filterKeys);
                });
            });
            $scope.facetFilterItems = function(query) {
                $scope.facetInstances = MagicSearchFilterService.facetFilterItems(query, $scope.instanceList);
                $scope.searchFilterItems();
            };
            /*  Filter items client side based on search criteria.
             */
            $scope.searchFilterItems = function(filterKeys) {
                $scope.filteredInstances = MagicSearchFilterService.searchFilterItems($scope.searchFilter, filterKeys, $scope.facetInstances);
            };
            $scope.filteredInstances = $scope.facetInstances = $scope.instanceList;
        }]
    };
}]);
