/**
 * @fileOverview Scaling groups landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('ScalingGroupsPage', ['LandingPage'])
    .controller('ScalingGroupsCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.scalinggroupID = '';
        $scope.scalinggroupName = '';
        $scope.scalinggroupInstances = '';
        $scope.revealModal = function (action, scalinggroup) {
            var modal = $('#' + action + '-scalinggroup-modal');
            $scope.scalinggroupID = scalinggroup['id'];
            $scope.scalinggroupName = scalinggroup['name'];
            $scope.scalinggroupInstances = scalinggroup['current_instances_count'];
            modal.foundation('reveal', 'open');
        };
    })
;

