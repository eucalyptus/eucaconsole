/**
 * @fileOverview IAM Group Detaile Page JS
 * @requires AngularJS
 *
 */

angular.module('GroupsPage', ['LandingPage'])
    .controller('GroupsCtrl', function ($scope, $timeout) {
        $scope.group_name = '';
        $scope.initPage = function () {
        };
        $scope.revealModal = function (action, group) {
            var modal = $('#' + action + '-group-modal');
            $scope.group_name = group['group_name'];
            modal.foundation('reveal', 'open');
            var form = $('#delete-form');
            var action = form.attr('action').replace("_name_", group['group_name']);
            form.attr('action', action);
        };
    })
;



