/**
 * @fileOverview IAM Account Detail Page JS
 * @requires AngularJS
 *
 */

angular.module('AccountsPage', ['LandingPage'])
    .controller('AccountsCtrl', function ($scope, $http, $timeout) {
        $scope.accountName = '';
        $scope.accountViewUrl = '';
        $scope.accountSummaryUrl = '';
        $scope.initPage = function (accountViewUrl, accountSummaryUrl) {
            $scope.accountViewUrl = accountViewUrl;
            $scope.accountSummaryUrl = accountSummaryUrl;
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
        $scope.$on('itemsLoaded', function($event, items) {
            for (var i=0; i < items.length; i++) {
                var url = $scope.accountSummaryUrl.replace('_name_', items[i].account_name);
                var theItems = items;
                $http.get(url).success(function(oData) {
                    var results = oData ? oData.results : [];
                    // search item list for this account
                    for (var k=0; k<theItems.length; k++) {
                        if (theItems[k].account_name == results.account_name) {
                            // add these values to the item record so that angular will see them
                            theItems[k].user_count = results.user_count;
                            theItems[k].group_count = results.group_count;
                            theItems[k].role_count = results.role_count;
                            break;
                        }
                    }
                }).error(function (oData, status) {
                    var errorMsg = oData['message'] || null;
                });
            }
        });
    })
;



