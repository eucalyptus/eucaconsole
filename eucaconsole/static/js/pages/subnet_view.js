/**
 * Copyright 2017 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Subnet Details Page JS
 * @requires AngularJS
 *
 */

angular.module('SubnetDetailsPage', ['TagEditorModule', 'InstancesServiceModule', 'EucaConsoleUtils', 'smart-table'])
    .controller('SubnetDetailsPageCtrl', function ($rootScope, $http, $timeout, InstancesService,
                                                   eucaUnescapeJson, eucaHandleError) {
        var vm = this;
        vm.instancesLoading = true;
        vm.terminatingInstance = false;
        vm.selectedInstance = {};
        vm.subnetInstances = [];
        vm.subnetInstanceLimit = 25;  // Limit subnet instances table to 25 rows
        vm.terminatedInstanceNotice = '';
        vm.subnetId = '';
        vm.removedTerminatedInstanceNotice = '';

        vm.init = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            vm.subnetId = options.subnet_id;
            vm.terminatedInstanceNotice = options.terminated_instance_notice;
            vm.removedTerminatedInstanceNotice = options.removed_terminated_instance_notice;
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

        vm.openTerminateInstanceDialog = function (instance) {
            vm.selectedInstance = instance;
            $('#terminate-instance-modal').foundation('reveal', 'open');
        };

        vm.terminateInstance = function ($event, instance, removeFromView) {
            $event.preventDefault();
            removeFromView = removeFromView || false;
            vm.terminatingInstance = true;
            var csrfToken = $('#csrf_token').val();
            var params = {'instance_id': instance.id};

            InstancesService.terminateInstance(csrfToken, params).then(
                function success() {
                    vm.terminatingInstance = false;
                    $('#terminate-instance-modal').foundation('reveal', 'close');
                    $rootScope.$broadcast('instanceTerminated');
                    if (removeFromView) {
                        Notify.success(vm.removedTerminatedInstanceNotice);
                    } else {
                        Notify.success(vm.terminatedInstanceNotice);
                    }
                },
                function error(errData) {
                    vm.terminatingInstance = false;
                    eucaHandleError(errData.data.message, errData.status);
                }
            );
        };

        vm.setWatch = function () {
            $rootScope.$on('instanceTerminated', function () {
                vm.fetchSubnetInstances();
            });
        };

    })
;
