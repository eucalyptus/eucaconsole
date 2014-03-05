/**
 * @fileOverview Key pairs landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('KeypairsPage', ['LandingPage'])
    .controller('KeypairsCtrl', function ($scope) {
        $scope.keypairName= '';
        $scope.revealModal = function (action, keypairName) {
            keypairName = keypairName || '';
            var modal = $('#' + action + '-keypair-modal');
            $scope.keypairName = keypairName;
            modal.foundation('reveal', 'open');
        };
    });

