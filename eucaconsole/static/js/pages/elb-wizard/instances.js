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
        // using $watch instead of ng-change because...
        // https://github.com/leocaseiro/angular-chosen/issues/145
        $scope.$watch('instances.availabilityZones', function(newval, oldval) {
            if (newval === oldval) return;  // leave unless there's a change
            vm.handleDeselectionDueToZones(newval, oldval);
        });
        vm.handleDeselectionDueToZones = function(newval, oldval) {
            var zoneDiff = oldval.filter(function(x) {
                var idx = newval.findIndex(function(val) {
                    return val.id === x.id;
                });
                return idx === -1;
            });
            if (zoneDiff.length === 0) return;  // leave unless there were zone(s) removed
            vm.instances.forEach(function(instance) {
                if (instance.selected !== true) return;  // get out fast if not selected
                var instanceInZone = zoneDiff.some(function(zone) {
                    return (zone.id === instance.availability_zone);
                });
                if (instanceInZone) instance.selected = false;
            });
        };
        $scope.$watch('instances.vpcSubnets', function(newval, oldval) {
            if (newval === oldval) return;  // leave unless there's a change
            vm.handleDeselectionDueToSubnets(newval, oldval);
        });
        vm.handleDeselectionDueToSubnets = function(newval, oldval) {
            var subnetDiff = oldval.filter(function(x) {
                var idx = newval.findIndex(function(val) {
                    return val.id === x.id;
                });
                return idx === -1;
            });
            if (subnetDiff.length === 0) return;  // leave unless there were subnet(s) removed
            vm.instances.forEach(function(instance) {
                if (instance.selected !== true) return;  // get out fast if not selected
                var instanceInSubnet = subnetDiff.some(function(subnet) {
                    return (subnet.id === instance.subnet_id);
                });
                if (instanceInSubnet) instance.selected = false;
            });
        };
        // may want to make this event-driven by having instance selector use callback upon selection change
        $scope.$watch('instances.instances', function(newval, oldval) {
            if (newval === oldval) return;  // leave unless there's a change
            vm.handleInstanceSelectionChange(newval, oldval);
        }, true);
        vm.handleInstanceSelectionChange = function(newval, oldval) {
            if (vm.vpcNetwork === 'None') {
                // update labels, accumulate zones for selection
                var zonesToSelect = [];
                vm.availabilityZoneChoices.forEach(function (zone) {
                    var count = vm.instances.filter(function(instance) {
                        return instance.selected && instance.availability_zone === zone.id;
                    }).length;
                    zone.label = zone.id + " : " + count + " instances";
                    if (count > 0) {
                        zonesToSelect.push(zone);
                    }
                });
                // update selection
                vm.availabilityZones = zonesToSelect;
            } else {
                // update labels, accumulate subnets for selection
                var subnetsToSelect = [];
                vm.vpcSubnetChoices.forEach(function (subnet) {
                    var count = vm.instances.filter(function(instance) {
                        return instance.selected && instance.subnet_id === subnet.id;
                    }).length;
                    subnet.label = subnet.labelBak + " : " + count + " instances";
                    if (count > 0) {
                        subnetsToSelect.push(subnet);
                    }
                });
                // update selection
                vm.vpcSubnets = subnetsToSelect;
            }
        };
        vm.submit = function () {
            if(vm.instanceForm.$invalid) {
                return;
            }
            ELBWizardService.next({});
        };
    }
]);
