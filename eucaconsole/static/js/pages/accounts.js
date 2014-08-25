/**
 * @fileOverview IAM Account Detail Page JS
 * @requires AngularJS
 *
 */

angular.module('AccountsPage', ['LandingPage'])
    .controller('AccountsCtrl', function ($scope, $timeout) {
        $scope.accountName = '';
        $scope.accountViewUrl = '';
        $scope.initPage = function (accountViewUrl) {
            $scope.accountViewUrl = accountViewUrl;
        };
        $scope.revealModal = function (action, account) {
            var modal = $('#' + action + '-account-modal');
            $scope.accountName = account['account_name'];
            modal.foundation('reveal', 'open');
            var form = $('#delete-form');
            var action = form.attr('action').replace("_name_", account['account_name']);
            form.attr('action', action);
        };
        $scope.linkAccount = function (account, fragment) {
            window.location = $scope.accountViewUrl.replace('_name_', account['account_name'])+fragment;
        };
    })
;



