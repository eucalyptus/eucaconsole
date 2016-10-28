/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview AngularJS elb wizard instance tab controller
 * @requires AngularJS
 *
 */

angular.module('ELBWizard')
.controller('InstancesController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    $scope.vpcNetwork = 'None';
    $scope.availabilityZones = [];
    $scope.availabilityZoneChoices = [{id:'one', label:'one'}];
    $scope.vpcSubnetChoices = [{id:'default', label:'default'}];
    $scope.selectedInstances = [];
}]);
