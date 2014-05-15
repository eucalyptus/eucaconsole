/**
 * @fileOverview Volumes landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('VolumesPage', ['LandingPage'])
    .controller('VolumesCtrl', function ($scope, $http, $timeout) {
        $scope.volumeID = '';
        $scope.volumeName = '';
        $scope.volumeZone = '';
        $scope.instanceName = '';
        $scope.instancesByZone = '';
        $scope.instanceChoices = {};
        $scope.initPage = function (instancesByZone) {
            $scope.instancesByZone = instancesByZone;
        };
        $scope.revealModal = function (action, volume) {
            var modal = $('#' + action + '-volume-modal'),
                volumeZone = volume['zone'];
            $scope.volumeID = volume['id'];
            $scope.volumeName = volume['name'];
            if (action === 'detach') {
                $scope.instanceName = volume['instance_name'];
            }
            if (action === 'attach') {
                // Set instance choices for attach to instance widget
                modal.on('open', function() {
                    $scope.instanceChoices = {};
                    var instancesByZone = $scope.instancesByZone[volumeZone],
                        instanceSelect = modal.find('#instance_id');
                    if (!!instancesByZone) {
                        instancesByZone.forEach(function (instance) {
                            $scope.instanceChoices[instance['id']] = instance['name'];
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
        $scope.detachModal = function (item, url) {
            $scope.volumeID = item['id'];
            $scope.instanceName = item.instance_name;
            url = url.replace('_id_', item.instance);
            $http.get(url).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    if (results.root_device_name == item.device) {
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

