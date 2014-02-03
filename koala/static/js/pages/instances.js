/**
 * @fileOverview Instances landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('InstancesPage', ['LandingPage'])
    .controller('InstancesCtrl', function ($scope) {
        $scope.instanceID = '';
        $scope.revealModal = function (action, instance) {
            var modal = $('#' + action + '-instance-modal');
            $scope.instanceID = instance['id'];
            $scope.rootDevice = instance['root_device'];
            modal.foundation('reveal', 'open');
        };
    })
;

