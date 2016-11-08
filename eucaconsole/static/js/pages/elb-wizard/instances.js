/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview AngularJS elb wizard instance tab controller
 * @requires AngularJS
 *
 */

angular.module('ELBWizard')
.controller('InstancesController', ['$scope', '$routeParams', 'eucaHandleError',
            'ELBWizardService',
    function ($scope, $routeParams, eucaHandleError, ELBWizardService) {
        var vm = this;
        vm.vpcNetwork = ELBWizardService.values.vpcNetwork;
        vm.availabilityZones = ELBWizardService.values.availabilityZones;
        vm.availabilityZoneChoices = ELBWizardService.values.availabilityZoneChoices;
        vm.vpcSubnets = ELBWizardService.values.vpcSubnets;
        vm.vpcSubnetChoices = ELBWizardService.values.vpcSubnetChoices;
        vm.instances = ELBWizardService.values.instances;
        vm.instancesLoading = (ELBWizardService.values.instances === undefined);
        vm.handleZoneChange = function() {
        };
        vm.handleSubnetChange = function() {
        };
        vm.submit = function () {
            if(vm.instanceForm.$invalid) {
                return;
            }
            ELBWizardService.next({});
        };
    }
]);
