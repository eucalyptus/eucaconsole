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
        // using $watch instead of ng-change because...
        // https://github.com/leocaseiro/angular-chosen/issues/145
        $scope.$watch('instances.vpcSubnets', function(newval, oldval) {
            if (newval == oldval) return;  // leave unless there's a change
            var subnetDiff = oldval.filter(function(x) {
                var idx = newval.indexOf(x);
                return newval.indexOf(x) === -1;
            });
            if (subnetDiff.length === 0) return;  // leave unless there were subnet(s) removed
            vm.instances.forEach(function(instance) {
                if (instance.selected !== true) return;  // get out fast if not selected
                var instanceInSubnet = subnetDiff.any(function(subnet) {
                    return (subnet.id === instance.subnet_id);
                });
                if (!instanceInSubnet) instance.selected = false;
            });
        });
        vm.submit = function () {
            if(vm.instanceForm.$invalid) {
                return;
            }
            ELBWizardService.next({});
        };
    }
]);
