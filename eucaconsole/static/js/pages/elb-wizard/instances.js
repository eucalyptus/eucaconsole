/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview AngularJS CloudWatch chart directive
 * @requires AngularJS, D3, nvd3.js
 *
 * Examples:
 * Fetch average CPU utilization percentage for instance 'i-foo' for the past hour
 * <svg cloudwatch-chart="" id="cwchart-cpu" class="cwchart" ids="i-foo" idtype="InstanceId"
 *      metric="CPUUtilization"duration="3600" unit="Percent" statistic="Average" />
 *
 */

angular.module('ELBWizard')
.controller('InstancesController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    $scope.vpcNetwork = 'Default';
    $scope.availabilityZones = [];
    $scope.availabilityZoneChoices = [{id:'one', label:'one'}];
    $scope.vpcSubnetChoices = [{id:'default', label:'default'}];
}]);
