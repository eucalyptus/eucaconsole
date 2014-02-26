/**
 * @fileOverview Users landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('UsersPage', ['LandingPage'])
    .controller('UsersCtrl', function ($scope, $http) {
        $scope.user_name = '';
        $scope.groupName = '';
        $scope.user_view_url = '';
        $scope.group_view_url = '';
        $scope.user_summary_url = '';
        $scope.initPage = function (user_view_url, group_view_url, user_summary_url) {
            $scope.user_view_url = user_view_url;
            $scope.group_view_url = group_view_url;
            $scope.user_summary_url = user_summary_url;
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
        $scope.$on('itemsLoaded', function($event, items) {
            console.log("items loaded!");
            for (var i=0; i < items.length; i++) {
                var url = $scope.user_summary_url.replace('_name_', items[i].user_name);
                var theItems = items;
                $http.get(url).success(function(oData) {
                    var results = oData ? oData.results : [];
                    // search item list for this user
                    for (var k=0; k<theItems.length; k++) {
                        if (theItems[k].user_name == results.user_name) {
                            // add these values to the item record so that angular will see them
                            theItems[k].has_password = results.has_password;
                            theItems[k].num_keys = results.num_keys;
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
