/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview AngularJS elb wizard instance tab controller
 * @requires AngularJS
 *
 */

angular.module('ELBWizard')
.controller('InstancesController', ['$scope', '$routeParams', 'InstancesService', 'eucaHandleError',
            'ELBWizardService',
    function ($scope, $routeParams, InstancesService, eucaHandleError, ELBWizardService) {
        var vm = this;
        vm.vpcNetwork = 'None';
        vm.availabilityZones = [];
        vm.availabilityZoneChoices = [{id:'one', label:'one'}];
        vm.vpcSubnetChoices = [{id:'default', label:'default'}];
        vm.instances = [];
        InstancesService.getInstances($('#csrf_token').val()).then(
            function success(result) {
                result.forEach(function(val) { vm.instances.push(val); });
                vm.instancesLoading = false;
            },
            function error(errData) {
                eucaHandleError(errData.data.message, errData.status);
                vm.instancesLoading = false;
            });
        vm.submit = function () {
            if(vm.instanceForm.$invalid) {
                return;
            }
            ELBWizardService.next({});
        };
    }
]);
