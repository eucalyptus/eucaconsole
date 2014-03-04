/**
 * @fileOverview Key pairs landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('KeypairsPage', ['LandingPage'])
    .controller('KeypairsCtrl', function ($scope) {
        $scope.keypairName= '';
        $scope.revealModal = function (action, keypair_name) {
            keypair_name = keypair_name || '';
            var modal = $('#' + action + '-keypair-modal');
            $scope.keypairName = keypair_name;
        };
    });

