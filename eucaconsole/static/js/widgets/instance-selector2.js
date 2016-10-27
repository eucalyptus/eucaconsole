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
        controller: ['$scope', 'InstancesService', 'eucaHandleError', function ($scope, InstancesService, eucaHandleError) {
            InstancesService.getInstances($('#csrf_token').val()).then(
                function success(result) {
                    $scope.instanceList = result;
                    $scope.instancesLoading = false;
                },
                function error(errData) {
                    eucaHandleError(errData.data.message, errData.status);
                    $scope.instancesLoading = false;
                });
            $scope.instancesLoading = true;
        }]
    }
}]);
