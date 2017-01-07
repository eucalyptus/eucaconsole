/**
 * Copyright 2017 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Subnet Details Page JS
 * @requires AngularJS
 *
 */

angular.module('SubnetDetailsPage', ['TagEditorModule', 'EucaConsoleUtils'])
    .controller('SubnetDetailsPageCtrl', function ($http, $timeout, eucaUnescapeJson) {
        var vm = this;
        vm.instancesLoading = true;
        vm.subnetInstances = [];

        vm.init = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            vm.fetchSubnetInstances(options.subnet_instances_json_url);
        };

        vm.fetchSubnetInstances = function (jsonUrl) {
            // May want to move this to a service, but since it's only used on the
            //   subnet details page let's inline it for now.
            $http.get(jsonUrl).success(function(oData) {
                var transitionalCount = oData ? oData.transitional_count : 0;
                vm.subnetInstances = oData ? oData.results : [];
                vm.instancesLoading = false;
                if (transitionalCount > 0) {
                    $timeout(function () {
                        vm.fetchSubnetInstances(jsonUrl);
                    }, 5000); // Poll every 5 seconds
                }
            });
        }
    })
;
