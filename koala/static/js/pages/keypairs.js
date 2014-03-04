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
    });

