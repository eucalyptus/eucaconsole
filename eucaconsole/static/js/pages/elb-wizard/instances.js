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
            vm.handleDeselection(newval, oldval, 'availability_zone');
        });
        $scope.$watch('instances.vpcSubnets', function(newval, oldval) {
            if (newval === oldval) return;  // leave unless there's a change
            vm.handleDeselection(newval, oldval, 'subnet_id');
        });
        vm.handleDeselection = function(newval, oldval, field) {
            var valDiff = oldval.filter(function(x) {
                var idx = newval.findIndex(function(val) {
                    return val.id === x.id;
                });
                return idx === -1;
            });
            if (valDiff.length === 0) return;  // leave unless there were zone(s) removed
            vm.instances.forEach(function(instance) {
                if (instance.selected !== true) return;  // get out fast if not selected
                var instanceInDeselectedVal = valDiff.some(function(zone) {
                    return (zone.id === instance[field]);
                });
                if (instanceInDeselectedVal) instance.selected = false;
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
                vm.availabilityZones = changeSelection(vm.availabilityZoneChoices, 'availability_zone', 'id');
            } else {
                // update labels, accumulate subnets for selection
                vm.vpcSubnets = changeSelection(vm.vpcSubnetChoices, 'subnet_id', 'labelBak');
            }
        };
        var changeSelection = function(resourceList, instanceField, resourceLabelBase) {
            var resourcesToSelect = [];
            resourceList.forEach(function (resource) {
                var count = vm.instances.filter(function(instance) {
                    return instance.selected && instance[instanceField] === resource.id;
                }).length;
                resource.label = resource[resourceLabelBase] + " : " + count + " instances";
                if (count > 0) {
                    resourcesToSelect.push(resource);
                }
            });
            return resourcesToSelect;
        };
        vm.submit = function () {
            if($scope.instanceForm.$invalid) {
                return;
            }
            ELBWizardService.next({});
        };
    }
]);
