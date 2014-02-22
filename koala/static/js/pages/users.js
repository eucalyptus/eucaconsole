/**
 * @fileOverview Users landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('UsersPage', ['LandingPage'])
    .controller('UsersCtrl', function ($scope) {
        $scope.user_name = '';
        $scope.groupName = '';
        $scope.user_view_url = '';
        $scope.group_view_url = '';
        $scope.initPage = function (user_view_url, group_view_url) {
            $scope.user_view_url = user_view_url;
            $scope.group_view_url = group_view_url;
        };
        $scope.revealModal = function (action, user) {
            var modal = $('#' + action + '-user-modal');
            $scope.user_name = user['user_name'];
            modal.foundation('reveal', 'open');
            var form = $('#delete-form');
            var action = form.attr('action').replace("_name_", user['user_name']);
            form.attr('action', action);
        };
        $scope.linkUser = function (user, fragment) {
            window.location = $scope.user_view_url.replace('_name_', user['user_name'])+fragment;
        };
    })
;
