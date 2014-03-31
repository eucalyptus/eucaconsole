/**
 * @fileOverview IAM Group Detaile Page JS
 * @requires AngularJS
 *
 */

angular.module('GroupsPage', ['LandingPage'])
    .controller('GroupsCtrl', function ($scope, $timeout) {
        $scope.groupName = '';
        $scope.groupViewUrl = '';
        $scope.initPage = function (groupViewUrl) {
            $scope.groupViewUrl = groupViewUrl;
        };
        $scope.revealModal = function (action, group) {
            var modal = $('#' + action + '-group-modal');
            $scope.groupName = group['group_name'];
            modal.foundation('reveal', 'open');
            var form = $('#delete-form');
            var action = form.attr('action').replace("_name_", group['group_name']);
            form.attr('action', action);
        };
        $scope.linkGroup = function (group, fragment) {
            window.location = $scope.groupViewUrl.replace('_name_', group['group_name'])+fragment;
        };
    })
;



