/**
 * @fileOverview Manage Credentials page JS
 * @requires AngularJS
 *
 */

angular.module('ManageCredentialsView', [])
    .directive('passwordStrength', function () {
        return {
            restrict: 'A',
            controller: ['$scope', function ($scope) {
                this.update = function (score) {
                    $scope.score = score;
                };
                $scope.strengthLabel = function () {
                    var score = $scope.score;
                    if (score === 0) word = 'weak';
                    if (score === 1 || score === 2) word = 'medium';
                    if (score === 3 || score === 4) word = 'strong';
                    if (score === undefined) word = 'none';
                    return 'password-' + word;
                };
            }]
        };
    })
    .directive('strength', function () {
        return {
            restrict: 'A',
            require: ['ngModel', '^passwordStrength'],
            link: function (scope, element, attrs, ctrl) {
                var passwordCtrl = ctrl[1];

                element.bind('keyup', function () {
                    var value = element.val();
                    scope.score = zxcvbn(value).score;
                    passwordCtrl.update(scope.score);
                });
            }
        };
    })
    .directive('match', function () {
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function (scope, element, attrs, ctrl) {
                var target = attrs.match;

                ctrl.$validators.match = function (modelValue) {
                    if(ctrl.$isEmpty(modelValue)) {
                        return true;
                    }
                    return modelValue === scope[target];
                };
            }
        };
    })
    .directive('nomatch', function () {
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function (scope, element, attrs, ctrl) {
                var target = attrs.nomatch;

                ctrl.$validators.nomatch = function (modelValue) {
                    if(ctrl.$isEmpty(modelValue)) {
                        return true;
                    }
                    return modelValue !== scope[target];
                };
            }
        };
    })
    .controller('ManageCredentialsViewCtrl', ['$scope', '$http', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

        $scope.isDisabled = function () {
            return $scope.eucaChangePassword.$invalid;
        };

        $scope.generateKeys = function(url) {
            var csrf_token = $('input[name="csrf_token"]').val();
            var data = "csrf_token="+csrf_token;
            $http({method:'POST', url: url, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                $('#create-keys-modal').foundation('reveal', 'close');
                Notify.success(oData.message);
                $scope.access_key = results.access;
                $scope.secret_key = results.secret;
            }).error(function (oData, status) {
                var errorMsg = oData.message || '';
                if (errorMsg == 'Session Timed Out' && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
                else if (status === 409) {
                    Notify.failure(errorMsg);
                }
                else {
                    $('#denied-keys-modal').foundation('reveal', 'open');
                }
            });
            return false;
        };

        $scope.downloadKeys = function(url) {
            var csrf_token = $('input[name="csrf_token"]').val();
            $.generateFile({
                csrf_token: csrf_token,
                filename: 'not-used', // let the server set this
                content: 'none',
                script: url
            });
        };

        $scope.cancelManageCredentialsUpdate = function () {
            window.history.back();
        };
    }])
; 
