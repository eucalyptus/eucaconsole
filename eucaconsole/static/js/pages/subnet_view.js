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
        vm.selectedInstance = {};
        vm.subnetInstances = [];
        vm.subnetInstanceLimit = 25;  // Limit subnet instances table to 25 rows
        vm.subnetId = '';

        vm.init = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            vm.subnetId = options.subnet_id;
            vm.fetchSubnetInstances();
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


    })
;
