/**
 * @fileOverview New user page JS
 * @requires AngularJS
 *
 */

// New user page includes the User Editor editor
angular.module('UserNew', ['UserEditor', 'Quotas', 'EucaConsoleUtils'])
    .controller('UserNewCtrl', function ($scope, $http, eucaHandleError) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.form = $('#user-new-form');
        $scope.submitEndpoint = '';
        $scope.allUsersRedirect = '';
        $scope.singleUserRedirect = '';
        $scope.accountRedirect = '';
        $scope.quotas_expanded = false;
        $scope.isNotValid = true;
        $scope.toggleQuotasContent = function () {
            $scope.quotas_expanded = !$scope.quotas_expanded;
        };
        $scope.toggleAdvContent = function () {
            $scope.adv_expanded = !$scope.adv_expanded;
        };
        $scope.initController = function(submitEndpoint, allRedirect, singleRedirect, accountRedirect, getFileEndpoint) {
            $scope.submitEndpoint = submitEndpoint;
            $scope.allUsersRedirect = allRedirect;
            $scope.singleUserRedirect = singleRedirect;
            $scope.accountRedirect = accountRedirect;
            $scope.getFileEndpoint = getFileEndpoint;
            $scope.setWatch();
            var as_acct = $('#as_account')
            if (as_acct.length > 0) {
                as_acct.chosen({'width': '200px', 'search_contains': true});
            }
            $('#user-name-field').focus();
        }
        $scope.setWatch = function () {
            $scope.$on('userAdded', function () {
                $scope.isNotValid = false;
            });
            $scope.$on('emptyUsersArray', function () {
                $scope.isNotValid = true;
            });
        };
        $scope.submit = function($event) {
            // Handle the unsaved user issue
            if($('#user-name-field').val() !== ''){
                $event.preventDefault(); 
                $('#unsaved-user-warn-modal').foundation('reveal', 'open');
                return false;
            }
            var form = $($event.target);
            $('#user-list-error').css('display', 'none');
            $('#quota-error').css('display', 'none');
            var users = JSON.parse(form.find('textarea[name="users"]').val())
            var singleUser = Object.keys(users)[0]
            if (singleUser === undefined) {
                $('#user-list-error').css('display', 'block');
                return;
            }
            var invalid = form.find('input[data-invalid]');
            if (invalid.length > 0) {
                $('#quota-error').css('display', 'block');
                return false;
            }
            var isSingleUser = Object.keys(users).length == 1;
            var as_account = $('#as_account').val();
            var csrf_token = form.find('input[name="csrf_token"]').val();
            var data = $($event.target).serialize();
            $http({method:'POST', url:$scope.submitEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                Notify.success(oData.message);
                if (results.hasFile == 'y') {
                    $('#new_password').val("");
                    $('#new_password2').val("");
                    $('#password-strength').removeAttr('class');
                    $.generateFile({
                        csrf_token: csrf_token,
                        filename: 'not-used', // let the server set this
                        content: 'none',
                        script: $scope.getFileEndpoint
                    });
                    // this is clearly a hack. We'd need to bake callbacks into the generateFile
                    // stuff to do this properly.
                    setTimeout(function() {
                        if (as_account === undefined) {
                            if (isSingleUser) {
                                window.location = $scope.singleUserRedirect.replace('_name_', singleUser);
                            } else {
                                window.location = $scope.allUsersRedirect;
                            }
                        } else {
                            window.location = $scope.accountRedirect.replace('_name_', as_account);
                        }
                    }, 3000);
                }
                else {
                    if (as_account === undefined) {
                        if (isSingleUser) {
                            window.location = $scope.singleUserRedirect.replace('_name_', singleUser);
                        } else {
                            window.location = $scope.allUsersRedirect;
                        }
                    } else {
                        window.location = $scope.accountRedirect.replace('_name_', as_account);
                    }
                }
            }).error(function (oData, status) {
                eucaHandleError(oData, status);
            });
        };
    })
;

