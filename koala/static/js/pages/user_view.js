/**
 * @fileOverview user view page JS
 * @requires AngularJS
 *
 */

// user view page includes the User Editor editor
angular.module('UserView', [])
    .controller('UserViewCtrl', function ($scope) {
        $scope.form = $('#user-update-form');
        $scope.ec2_expanded = false;
        $scope.s3_expanded = false;
        $scope.autoscale_expanded = false;
        $scope.elb_expanded = false;
        $scope.iam_expanded = false;
        $scope.toggleEC2Content = function () {
            $scope.ec2_expanded = !$scope.ec2_expanded;
        };
        $scope.toggleS3Content = function () {
            $scope.s3_expanded = !$scope.s3_expanded;
        };
        $scope.toggleAutoscaleContent = function () {
            $scope.autoscale_expanded = !$scope.autoscale_expanded;
        };
        $scope.toggleELBContent = function () {
            $scope.elb_expanded = !$scope.elb_expanded;
        };
        $scope.toggleIAMContent = function () {
            $scope.iam_expanded = !$scope.iam_expanded;
        };
    })
    .controller('UserUpdateCtrl', function($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.jsonEndpoint = '';
        $scope.initController = function (jsonEndpoint) {
            $scope.jsonEndpoint = jsonEndpoint;
        };
        $scope.submit = function($event) {
            var data = $($event.target).serialize();
            $http({method:'POST', url:$scope.jsonEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                // could put data back into form, but form already contains changes
                // TODO: how to notify user of success??
              }).
              error(function (oData, status) {
                var errorMsg = oData['error'] || null;
                // TODO: properly handle error notifications
                if (errorMsg && status === 403) {
                    // not authorized
                    alert(errorMsg);
                } else {
                    // other kind of error
                }
              });
        };
    })
    .controller('UserPasswordCtrl', function($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.jsonEndpoint = '';
        $scope.data = '';
        $scope.initController = function (jsonEndpoint) {
            $scope.jsonEndpoint = jsonEndpoint;
            var newPasswordForm = $('#new_password');
            // add password strength meter to first new password field
            newPasswordForm.after("<hr id='password-strength'/>");
            newPasswordForm.on('keypress', function () {
                var val = $(this).val();
                var score = zxcvbn(val).score;
                $('#password-strength').attr('class', "password_" + score);
            });
            $("#change-password-modal").on('show', function () {
                $('#password').focus(); // doesn't seem to work.
            });
        };
        // Handles first step in submit.. validation and dialog
        $scope.submit = function($event) {
            $('#passwords-match').css('display', 'none');
            var newpass = $event.target.new_password.value;
            var newpass2 = $event.target.new_password2.value;
            if (newpass != newpass2) {
                $('#passwords-match').css('display', 'block');
                return false;
            }
            $scope.data = $($event.target).serialize();
            // open modal to get current password
            $('#change-password-modal').foundation('reveal', 'open');
        };
        // handles server call for changing the password
        $scope.changePassword = function($event) {
            // add in current password, then submit the request
            var data = $scope.data+"&password="+$event.target.password.value;
            $http({method:'POST', url:$scope.jsonEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                $('#change-password-modal').foundation('reveal', 'close');
                // clear form
                $('#new_password').val("");
                $('#new_password2').val("");
                $('#password-strength').removeAttr('class');
                // TODO: how to notify user of success??
              }).
              error(function (oData, status) {
                var errorMsg = oData['error'] || null;
                // TODO: properly handle error notifications
                if (status == 401) {
                    alert("Invalid password");
                }
                else if (errorMsg && status === 403) {
                    // not authorized
                    alert(errorMsg);
                } else {
                    // other kind of error
                }
              });
        };
    })
    .controller('UserAccessKeysCtrl', function($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.jsonEndpoint = '';
        $scope.jsonItemsEndpoint = '';
        $scope.items = [];
        $scope.itemsLoading = true;
        $scope.initController = function (jsonEndpoint, jsonItemsEndpoint) {
            $scope.jsonEndpoint = jsonEndpoint;
            $scope.jsonItemsEndpoint = jsonItemsEndpoint;
            $scope.getItems(jsonItemsEndpoint);
        };
        $scope.getItems = function (jsonItemsEndpoint) {
            $http.get(jsonItemsEndpoint).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = false;
                $scope.items = results;
            }).error(function (oData, status) {
                var errorMsg = oData['error'] || null;
                if (errorMsg && status === 403) {
                    alert(errorMsg);
                    $('#euca-logout-form').submit();
                }
            });
        };
        $scope.revealModal = function (modal, item) {
        };
        $scope.generateKeys = function ($event) {
            $http({method:'POST', url:$scope.jsonEndpoint, data:'',
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                // TODO: how to notify user of success??
                $scope.itemsLoading = true;
                $scope.items = [];
                $scope.getItems($scope.jsonItemsEndpoint);
              }).
              error(function (oData, status) {
                var errorMsg = oData['error'] || null;
                // TODO: properly handle error notifications
                if (errorMsg && status === 403) {
                    // not authorized
                    alert(errorMsg);
                } else {
                    // other kind of error
                }
              });
        };
    })
    .controller('UserGroupsCtrl', function($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.jsonEndpoint = '';
        $scope.jsonItemsEndpoint = '';
        $scope.items = [];
        $scope.itemsLoading = true;
        $scope.initController = function (jsonEndpoint, jsonItemsEndpoint) {
            $scope.jsonEndpoint = jsonEndpoint;
            $scope.jsonItemsEndpoint = jsonItemsEndpoint;
            $scope.getItems(jsonItemsEndpoint);
        };
        $scope.getItems = function (jsonItemsEndpoint) {
            $http.get(jsonItemsEndpoint).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = false;
                $scope.items = results;
            }).error(function (oData, status) {
                var errorMsg = oData['error'] || null;
                if (errorMsg && status === 403) {
                    alert(errorMsg);
                    $('#euca-logout-form').submit();
                }
            });
        };
        $scope.revealModal = function (modal, item) {
        };
        $scope.addUserToGroup = function ($event) {
            $http({method:'POST', url:$scope.jsonEndpoint, data:'',
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                // TODO: how to notify user of success??
                $scope.itemsLoading = true;
                $scope.items = [];
                $scope.getItems($scope.jsonItemsEndpoint);
              }).
              error(function (oData, status) {
                var errorMsg = oData['error'] || null;
                // TODO: properly handle error notifications
                if (errorMsg && status === 403) {
                    // not authorized
                    alert(errorMsg);
                } else {
                    // other kind of error
                }
              });
        };
    })
;

