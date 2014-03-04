/**
 * @fileOverview Instances landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('InstancesPage', ['LandingPage'])
    .controller('InstancesCtrl', function ($scope) {
        $scope.instanceID = '';
        $scope.batchTerminateModal = $('#batch-terminate-modal');
        $scope.initChosenSelectors = function () {
            $scope.batchTerminateModal.on('open', function () {
                var instanceIdsSelect = $scope.batchTerminateModal.find('select');
                instanceIdsSelect.chosen({'width': '100%', 'search_contains': true});
                instanceIdsSelect.trigger('chosen:updated');
            });
        };
        $scope.initController = function () {
            $scope.initChosenSelectors();
        };
        $scope.revealModal = function (action, instance) {
            var modal = $('#' + action + '-instance-modal');
            $scope.instanceID = instance['id'];
            $scope.rootDevice = instance['root_device'];
            modal.foundation('reveal', 'open');
            $scope.setFocus();
        };
        $scope.setFocus = function () {
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var inputElement = modal.find('input[type!=hidden]').get(0);
                if( inputElement != undefined ){
                    inputElement.focus()
                }else{
                    modal.find('button').get(0).focus();
                }
            });
        };
        $scope.unterminatedInstancesCount = function (items) {
            return items.filter(function (item) {
                return item.status !== 'terminated';
            }).length;
        }
    })
;

