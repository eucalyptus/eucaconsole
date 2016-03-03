/**
 * @fileOverview Key pairs landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('KeypairsPage', ['LandingPage', 'smart-table'])
    .controller('KeypairsCtrl', function ($scope) {
        $scope.keypairName= '';
        $scope.multipleItemsSelected = false;
        $scope.revealModal = function (action, keypairName) {
            keypairName = keypairName || '';
            var modal = $('#' + action + '-keypair-modal');
            $scope.keypairName = keypairName;
            modal.foundation('reveal', 'open');
        };
        $scope.revealMultiSelectModal = function (action, selectedItems) {
            var modal = $('#' + action + '-keypair-modal'),
                itemNames = [];
            selectedItems.forEach(function (item) {
                itemNames.push(item.name || item.id);
            });
            $scope.multipleItemsSelected = itemNames.length > 1;
            $scope.keypairName = itemNames.join(', ');
            modal.foundation('reveal', 'open');
        };
    });

