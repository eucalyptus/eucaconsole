/**
 * @fileOverview Volumes landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('VolumesPage', ['LandingPage'])
    .controller('VolumesCtrl', function ($scope) {
        $scope.volumeID = '';
        $scope.volumeZone = '';
        $scope.instancesByZone = '';
        $scope.initPage = function (instancesByZone) {
            $scope.instancesByZone = instancesByZone;
        };
        $scope.revealModal = function (action, volume) {
            var modal = $('#' + action + '-volume-modal'),
                volumeZone = volume['zone'];
            $scope.volumeID = volume['id'];
            if (action === 'attach') {
                // Set instance choices for attach to instance widget
                modal.on('open', function() {
                    var instanceSelect = $('#instance_id'),
                        instances = $scope.instancesByZone[volumeZone],
                        options = '';
                    if (instances === undefined) {
                        options = "<option value=''>No available instances in the same availability zone</option>";
                    }
                    else {
                      instances.forEach(function (instance) {
                          options += '<option value="' + instance['id'] + '">' + instance['name'] + '</option>';
                      });
                    }
                    instanceSelect.html(options);
                    instanceSelect.trigger('chosen:updated');
                    instanceSelect.chosen({'width': '75%', search_contains: true});
                });
            }
            modal.foundation('reveal', 'open');
            setTimeout(function(){
                    var inputElement = modal.find('input[type!=hidden]').get(0);
                    if( inputElement != undefined ){
                        inputElement.focus()
                    }else{
                        modal.find('button').get(0).focus();
                    }
                }, 1000);
        };
    })
;

