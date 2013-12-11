/**
 * @fileOverview Elastic IPs landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('ElasticIPsPage', ['LandingPage'])
    .controller('ElasticIPsCtrl', function ($scope) {
        $scope.publicIP = '';
        $scope.revealModal = function (action, eip) {
            var modal = $('#' + action + '-ip-modal');
            $scope.publicIP = eip;
            modal.foundation('reveal', 'open');
        };
    });

