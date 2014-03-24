/**
 * @fileOverview Volumes landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('VolumesPage', ['LandingPage'])
    .controller('VolumesCtrl', function ($scope, $timeout) {
        $scope.volumeID = '';
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
    })
;

