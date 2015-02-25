/**
 * @fileOverview CloudFormations landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('StacksPage', ['LandingPage'])
    .controller('StacksPageCtrl', function ($scope) {
        $scope.stackName = '';
        $scope.revealModal = function (action, stack) {
            $scope.stackName = stack.name;
            var modal = $('#' + action + '-stack-modal');
            modal.foundation('reveal', 'open');
        };
    });

