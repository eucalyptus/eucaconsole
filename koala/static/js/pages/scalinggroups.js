/**
 * @fileOverview Scaling groups landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('ScalinggroupsPage', ['LandingPage'])
    .controller('ScalinggroupsCtrl', function ($scope) {
        $scope.scalinggroupID = '';
        $scope.scalinggroupName = '';
        $scope.revealModal = function (action, scalinggroup) {
            var modal = $('#' + action + '-scalinggroup-modal');
            $scope.scalinggroupID = scalinggroup['id'];
            $scope.scalinggroupName = scalinggroup['name'];
            modal.foundation('reveal', 'open');
        };
    })
;

