/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview AngularJS elb wizard instance tab controller
 * @requires AngularJS
 *
 */

angular.module('ELBWizard')
.controller('InstancesController', ['$scope', '$routeParams', 'InstancesService', 'eucaHandleError', function ($scope, $routeParams, InstancesService, eucaHandleError) {
    $scope.vpcNetwork = 'None';
    $scope.availabilityZones = [];
    $scope.availabilityZoneChoices = [{id:'one', label:'one'}];
    $scope.vpcSubnetChoices = [{id:'default', label:'default'}];
    $scope.instances = [];
    $scope.$watch('instances', function(newval, oldval) {
        console.log('instances = '+newval);
        if (newval == oldval) {
            $scope.instances = [];
        }
    });
    InstancesService.getInstances($('#csrf_token').val()).then(
        function success(result) {
            $scope.instances.forEach(function() { $scope.instances.pop(); });
            result.forEach(function(val) { $scope.instances.push(val); });
            $scope.instancesLoading = false;
        },
        function error(errData) {
            eucaHandleError(errData.data.message, errData.status);
            $scope.instancesLoading = false;
        });
}]);
