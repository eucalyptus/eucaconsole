/**
 * @fileOverview Manage Credentials page JS
 * @requires AngularJS
 *
 */

angular.module('ManageCredentialsView', [])
    .controller('ManageCredentialsViewCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.initController = function() {
            var newPasswordForm = $('#new_password');
            // add password strength meter to first new password field
            newPasswordForm.after("<hr id='password-strength'/><span id='password-word'></span>");
            $('#password-strength').attr('class', "password_none");
            $('#password-word').text('');
            newPasswordForm.on('keypress', function () {
                var val = $(this).val();
                var score = zxcvbn(val).score;
                $('#password-strength').attr('class', "password_" + score);
                $('#password-word').attr('class', "password_" + score);
                var word = '';
                if (score == 0) word = 'weak';
                if (score == 1 || score == 2) word = 'medium';
                if (score == 3 || score == 4) word = 'strong';
                $('#password-word').text(word);
            });

            var form = $('#euca-changepassword-form');
            form.on('submit', function () {
                $('.error').css('display', 'none');
                var pass = $(this).find('#current_password').val();
                var newpass = $(this).find('#new_password').val();
                var newpass2 = $(this).find('#new_password2').val();
                if (pass == newpass) {
                    $('#password-different').css('display', 'block');
                    return false;
                }
                if (newpass != newpass2) {
                    $('#passwords-match').css('display', 'block');
                    return false;
                }
            });
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
                var errorMsg = oData['message'] || '';
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
                script: url,
            });
        };
    })
; 
