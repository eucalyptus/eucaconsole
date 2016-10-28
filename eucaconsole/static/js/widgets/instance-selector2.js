/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Instance Selector Directive JS
 * @requires AngularJS
 *
 */

angular.module('InstancesSelectorModule', ['InstancesServiceModule', 'EucaConsoleUtils'])
.directive('instanceSelector', [function() {
    return {
        restrict: 'E',
        scope: {
        },
        templateUrl: '/_template/elbs/instance-selector',
        controller: ['$scope', '$timeout', 'InstancesService', 'eucaHandleError', function ($scope, $timeout, InstancesService, eucaHandleError) {
            InstancesService.getInstances($('#csrf_token').val()).then(
                function success(result) {
                    $scope.instanceList = result;
                    $scope.instancesLoading = false;
                },
                function error(errData) {
                    eucaHandleError(errData.data.message, errData.status);
                    $scope.instancesLoading = false;
                });
            $scope.instanceList = [];
            $scope.instancesLoading = true;
            $scope.state = {'allSelected': false};
            $scope.setAllState = function() {
                $timeout(function() {
                    angular.forEach($scope.instanceList, function(item) {
                        item.selected = $scope.state.allSelected;
                    });
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
                $scope.selectedItems = checkedIems;
            };
        }]
    };
}]);
