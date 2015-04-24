/**
 * @fileOverview ELB landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('ELBsPage', ['LandingPage'])
    .controller('ELBsPageCtrl', function ($scope) {
        $scope.elbName = '';
        $scope.revealModal = function (action, elb) {
            $scope.elbName = elb.name;
            var modal = $('#' + action + '-elb-modal');
            modal.foundation('reveal', 'open');
        };
    });

