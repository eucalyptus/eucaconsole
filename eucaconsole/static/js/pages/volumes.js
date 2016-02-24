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
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.instancesByZone = options.instances_by_zone;
            $scope.instanceJsonUrl = options.instance_json_url;
        };
        $scope.revealModal = function (action, volume) {
            var modal = $('#' + action + '-volume-modal'),
                volumeZone = volume.zone;
            $scope.volumeID = volume.id;
            $scope.volumeName = volume.name;
            if (action === 'detach') {
                $scope.instanceName = volume.instance_name;
            }
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
                if (action === 'detach') {
                    instanceNames.push(item.instance_name);
                }
            });
            $scope.multipleItemsSelected = itemIDs.length > 1;
            $scope.volumeID = itemIDs.join(', ');
            $scope.volumeName = itemNames.join(', ');
            $scope.instanceName = instanceNames.join(', ');
            modal.foundation('reveal', 'open');
        };
        $scope.detachModal = function (item) {
            $scope.volumeID = item.id;
            $scope.volumeName = item.name;
            $scope.instanceName = item.instance_name;
            var url = $scope.instanceJsonUrl;
            url = url.replace('_id_', item.instance);
            $http.get(url).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    if (results.root_device_name === item.device) {
                        $('#detach-volume-warn-modal').foundation('reveal', 'open');
                    } else {
                        $('#detach-volume-modal').foundation('reveal', 'open');
                    }
                }
            });
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

