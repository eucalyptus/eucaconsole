/**
 * @fileOverview Users landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('UsersPage', ['LandingPage'])
    .controller('UsersCtrl', function ($scope) {
        $scope.user_name = '';
        $scope.initPage = function () {
        };
        $scope.revealModal = function (action, user) {
            var modal = $('#' + action + '-user-modal');
            $scope.user_name = user['user_name'];
            modal.foundation('reveal', 'open');
            var form = $('#delete-form');
            var action = form.attr('action').replace("_name_", user['user_name']);
            form.attr('action', action);
        };
    })
;
