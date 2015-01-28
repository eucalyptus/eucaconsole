/**
 * @fileOverview IAM Role Landing Page JS
 * @requires AngularJS
 *
 */

angular.module('RolesPage', ['LandingPage'])
    .controller('RolesCtrl', function ($scope, $timeout) {
        $scope.roleName = '';
        $scope.roleViewUrl = '';
        $scope.initPage = function (roleViewUrl) {
            $scope.roleViewUrl = roleViewUrl;
        };
        $scope.revealModal = function (action, role) {
            var modal = $('#' + action + '-role-modal');
            $scope.roleName = role['role_name'];
            modal.foundation('reveal', 'open');
            var form = $('#delete-form');
            if (form != null && form.attr('action') != undefined) {
                var action = form.attr('action').replace("_name_", role['role_name']);
                form.attr('action', action);
            }
        };
        $scope.linkRole = function (role, fragment) {
            window.location = $scope.roleViewUrl.replace('_name_', role['role_name'])+fragment;
        };
    })
;



