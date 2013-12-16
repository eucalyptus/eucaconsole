/**
 * @fileOverview Snapshots landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('SecurityGroupsPage', ['LandingPage'])
    .controller('SecurityGroupsCtrl', function ($scope) {
        $scope.securitygroupID = '';
        $scope.urlParams = $.url().param();
        $scope.displayType = $scope.urlParams['display'] || 'gridview';
        $scope.revealModal = function (action, securitygroup) {
            var modal = $('#' + action + '-securitygroup-modal');
            $scope.securitygroupID = securitygroup['id'];
            modal.foundation('reveal', 'open');
        };
    })
;