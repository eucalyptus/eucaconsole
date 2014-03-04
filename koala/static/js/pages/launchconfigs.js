/**
 * @fileOverview Launch configurations landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('LaunchConfigsPage', ['LandingPage'])
    .controller('LaunchConfigsPageCtrl', function ($scope) {
        $scope.launchConfigName= '';
        $scope.launchConfigInUse = false;
        $scope.revealModal = function (action, launchConfig) {
            $scope.launchConfigName = launchConfig['name'];
            $scope.launchConfigInUse = launchConfig['in_use'];
            var modal = $('#' + action + '-launchconfig-modal');
            modal.foundation('reveal', 'open');
        };
    });

