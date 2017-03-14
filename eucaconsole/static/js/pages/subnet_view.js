/**
 * Copyright 2017 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Subnet Details Page JS
 * @requires AngularJS
 *
 */

angular.module('SubnetDetailsPage',
    ['TagEditorModule', 'RouteTableEditorModule', 'InstancesServiceModule', 'EucaConsoleUtils', 'smart-table'])
    .controller('SubnetDetailsPageCtrl', function ($rootScope, $http, $timeout, InstancesService,
                                                   eucaUnescapeJson, eucaHandleError) {
        var vm = this;
        vm.instancesLoading = true;
        vm.sendingTerminateInstancesRequest = false;
        vm.selectedInstance = {};
        vm.subnetInstances = [];
        vm.nonTerminatedInstances = [];
        vm.subnetInstanceLimit = 25;  // Limit subnet instances table to 25 rows
        vm.terminatedInstancesNotice = '';
        vm.subnetId = '';

        vm.init = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            vm.terminatedInstancesNotice = options.terminated_instances_notice;
            vm.subnetId = options.subnet_id;
            vm.fetchSubnetInstances();
            vm.setWatch();
        };

        vm.fetchSubnetInstances = function () {
            var csrfToken = $('#csrf_token').val();
            var params = {'subnet_id': vm.subnetId};
            InstancesService.getInstances(csrfToken, params).then(
                function success(results) {
                    vm.instancesLoading = false;
                    vm.subnetInstances = results;
                    vm.nonTerminatedInstances = results.filter(function (instance) {
                        return instance.status !== 'terminated';
                    });
                    var transitionalCount = results.filter(function(instance) {
                        return instance.transitional;
                    }).length;
                    if (transitionalCount > 0) {
                        $timeout(function () {
                            vm.fetchSubnetInstances(vm.subnetId);
                        }, 5000); // Poll every 5 seconds
                    }
                },
                function error(errData) {
                    eucaHandleError(errData.data.message, errData.status);
                });
        };

        vm.terminateInstances = function ($event) {
            $event.preventDefault();
            vm.sendingTerminateInstancesRequest = true;
            var csrfToken = $('#csrf_token').val();
            var instanceIDs = vm.nonTerminatedInstances.map(function (instance) {
                return instance.id;
            }).join(',');
            var params = {'instance_id': instanceIDs};

            InstancesService.terminateInstances(csrfToken, params).then(
                function success() {
                vm.sendingTerminateInstancesRequest = false;
                    $('#delete-subnet-modal').foundation('reveal', 'close');
                    $rootScope.$broadcast('instancesTerminating');
                    Notify.success(vm.terminatedInstancesNotice);
                },
                function error(errData) {
                vm.sendingTerminateInstancesRequest = false;
                    eucaHandleError(errData.data.message, errData.status);
                }
            );
        };

        vm.setWatch = function () {
            $rootScope.$on('instancesTerminating', function () {
                vm.fetchSubnetInstances();
            });
        };
    })
;
