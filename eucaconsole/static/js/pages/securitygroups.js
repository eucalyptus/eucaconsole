/**
 * @fileOverview Security groups landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('SecurityGroupsPage', ['LandingPage', 'smart-table'])
    .controller('SecurityGroupsCtrl', function ($scope) {
        $scope.securitygroupID = '';
        $scope.multipleItemsSelected = false;
        $scope.revealModal = function (action, securitygroup) {
            var modal = $('#' + action + '-securitygroup-modal');
            $scope.securitygroupID = securitygroup.id;
            $scope.securitygroupName = securitygroup.name;
            modal.foundation('reveal', 'open');
        };
        $scope.revealMultiSelectModal = function (action, selectedItems) {
            var modal = $('#' + action + '-securitygroup-modal'),
                itemIDs = [],
                itemNames = [];
            selectedItems.forEach(function (item) {
                itemIDs.push(item.id);
                itemNames.push(item.name || item.id);
            });
            $scope.multipleItemsSelected = itemIDs.length > 1;
            $scope.securitygroupID = itemIDs.join(', ');
            $scope.securitygroupName = itemNames.join(', ');
            modal.foundation('reveal', 'open');
        };
    })
;
