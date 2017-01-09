/**
 * Copyright 2017 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Subnet Details Page JS
 * @requires AngularJS
 *
 */

angular.module('SubnetDetailsPage', ['TagEditorModule', 'InstancesServiceModule', 'EucaConsoleUtils'])
    .controller('SubnetDetailsPageCtrl', function ($http, $timeout, InstancesService, eucaUnescapeJson) {
        var vm = this;
        vm.instancesLoading = true;
        vm.subnetInstances = [];

        vm.init = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            vm.fetchSubnetInstances(options.subnet_id);
        };

        vm.fetchSubnetInstances = function (subnetId) {
            var csrfToken = $('#csrf_token').val();
            var params = {'subnet_id': subnetId};
            InstancesService.getInstances(csrfToken, params).then(
                function success(results) {
                    vm.instancesLoading = false;
                    vm.subnetInstances = results;
                    var transitionalCount = results.filter(function(instance) {
                        return instance.transitional;
                    }).length;
                    if (transitionalCount > 0) {
                        $timeout(function () {
                            vm.fetchSubnetInstances(subnetId);
                        }, 5000); // Poll every 5 seconds
                    }
                },
                function error(errData) {
                    eucaHandleError(errData.data.message, errData.status);
                });
        };
    })
;
