/**
 * @fileOverview Volumes landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('VolumesPage', ['LandingPage', 'EucaConsoleUtils', 'smart-table'])
    .controller('VolumesCtrl', function ($scope, $http, $timeout, eucaUnescapeJson) {
        $scope.volumeID = '';
        $scope.volumeName = '';
        $scope.volumeZone = '';
        $scope.instanceName = '';
        $scope.instancesByZone = '';
        $scope.instanceChoices = {};
        $scope.multipleItemsSelected = false;
        $scope.rootVolumes = [];
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.instancesByZone = options.instances_by_zone;
        };
        $scope.revealModal = function (action, volume) {
            var modal = $('#' + action + '-volume-modal'),
                volumeZone = volume.zone;
            $scope.volumeID = volume.id;
            $scope.volumeName = volume.name;
            if (action === 'attach') {
                // Set instance choices for attach to instance widget
                modal.on('open.fndtn.reveal', function() {
                    $scope.instanceChoices = {};
                    var instancesByZone = $scope.instancesByZone[volumeZone],
                        instanceSelect = modal.find('#instance_id');
                    if (!!instancesByZone) {
                        instancesByZone.forEach(function (instance) {
                            $scope.instanceChoices[instance.id] = instance.name;
                        });
                    } else {
                        $scope.instanceChoices[''] = 'No available instances in availability zone ' + volumeZone;
                    }
                    $timeout(function () {
                        instanceSelect.trigger('chosen:updated');
                        instanceSelect.chosen({'width': '75%', search_contains: true});
                    }, 50);
                });
            }
            modal.foundation('reveal', 'open');
        };
        $scope.revealMultiSelectModal = function (action, selectedItems) {
            var modal = $('#' + action + '-volume-modal');
            var itemIDs = [];
            var itemNames = [];
            var instanceNames = [];
            selectedItems.forEach(function (item) {
                itemIDs.push(item.id);
                itemNames.push(item.name || item.id);
            });
            $scope.multipleItemsSelected = itemIDs.length > 1;
            $scope.volumeID = itemIDs.join(', ');
            $scope.volumeName = itemNames.join(', ');
            $scope.instanceName = instanceNames.join(', ');
            modal.foundation('reveal', 'open');
        };
        $scope.revealMultiSelectDetachModal = function (selectedItems) {
            // Multi-select Detach operation requires special handling of root volumes in EBS-backed instances
            var modal = $('#detach-volume-modal');
            var itemIDs = [];
            var itemNames = [];
            var instanceNames = [];
            var rootVolumes = [];
            selectedItems.forEach(function (item) {
                if (item.is_root_volume) {
                    rootVolumes.push({
                        volume: item.name,
                        instance: item.instance_name
                    });
                } else {
                    itemIDs.push(item.id);
                    itemNames.push(item.name || item.id);
                    instanceNames.push(item.instance_name);
                }
            });
            $scope.multipleItemsSelected = selectedItems.length > 1;
            $scope.volumeID = itemIDs.join(', ');
            $scope.volumeName = itemNames.join(', ');
            $scope.instanceName = instanceNames.join(', ');
            $scope.rootVolumes = rootVolumes;
            modal.foundation('reveal', 'open');
        };
        $scope.detachModal = function (item) {
            // Handles Detach action from single item actions menu
            $scope.volumeID = item.id;
            $scope.volumeName = item.name;
            $scope.instanceName = item.instance_name;
            if (item.is_root_volume) {
                $('#detach-volume-warn-modal').foundation('reveal', 'open');
            } else {
                $('#detach-volume-modal').foundation('reveal', 'open');
            }
        };
        $scope.getDeviceSuggestion = function () {
            // TODO: the url shouldn't be built by hand, pass value from request.route_path!
            var instanceId = $('#instance_id').val();
            $http.get("/instances/"+instanceId+"/nextdevice/json").success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $('input#device').val(results);
                }
            });
        };
    })
;

