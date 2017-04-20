/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview Login page JS
 * @requires AngularJS
 *
 */

angular.module('LoginPage', ['EucaConsoleUtils'])
    .controller('LoginPageCtrl', function ($scope, $timeout, eucaUnescapeJson) {
        var accountField = $("#account");
        var usernameField = $("#username");
        var passwordField = $("#password");
        var accessKeyField = $("#access_key");
        var secretKeyField = $("#secret_key");
        var accountNameField = $("#account-name");
        $scope.showHttpsWarning = false;
        $scope.isLoggingIn = false;
        $scope.eucaNotValid = true;
        $scope.awsNotValid = true;
        $scope.oidcNotValid = true;
        $scope.initController = function (json_options) {
            var options = JSON.parse(eucaUnescapeJson(json_options));
            $scope.prefillForms(options.account, options.username);
            $scope.oidcLoginLink = options.oidcLoginLink;
            $scope.addListeners();
            Modernizr.load([
                {
                    test: Modernizr.svg,
                    nope: function () {
                        $('#browser-svg-warn-modal').foundation('reveal', 'open');
                    }
                },
                {
                    test: Modernizr.filereader,
                    nope: function () {
                        $('#browser-filereader-warn-modal').foundation('reveal', 'open');
                    }
                }
            ]);
            $scope.showHttpsWarning = window.location.protocol !== 'https:';
            // clear copy buffer for object storage
            if (Modernizr.sessionstorage) {
                sessionStorage.removeItem('copy-object-buffer');
            }
            var storedRegion = (Modernizr.localstorage && localStorage.getItem('euca-region')) || 'euca';
            $("#euca-region").val(storedRegion);
            $scope.oidcUrl = $scope.oidcLoginLink + "&state=oidc-" + $.base64.encode(storedRegion);
            $timeout(function() {  // this being delayed to allow browser to populate login form completely
                $scope.eucaCheckValid();
                $scope.awsCheckValid();
            }, 250);
        };
        $scope.setFocus = function () {
            var inputs = [];
            if ($('#eucalyptus').is(':visible')) {
                inputs = $('#euca-login-form').find('input').filter(function () {
                    return !this.value;
                });
                if (inputs.length > 0) inputs[0].focus();
            }
            if ($('#aws').is(':visible')) {
                inputs = $('#aws-login-form').find('input').filter(function () {
                    return !this.value;
                });
                if (inputs.length > 0) inputs[0].focus();
            }
        };
        $scope.prefillForms = function (url_account, url_username) {
            // pre-fill if cookies are present
            var last_login = $.cookie('login-form');
            var account = $.cookie('account');
            var username = $.cookie('username');
            if (url_account !== '') {
                account = url_account;
                if (url_username !== '') {
                    username = url_username;
                    $('#username').val(url_username);
                }
                last_login = 'euca';
            }
            if (account !== undefined) accountField.val(account);
            if (username !== undefined) usernameField.val(username);

            if (last_login == 'aws') {  // select that tab
                // all this mimics what happens in the tab code itself... no other way I found worked.
                var tab = $('#aws-tab');
                tab.addClass('active').trigger('opened');
                tab.siblings().removeClass('active');
                var target = $('#aws');
                target.siblings().removeClass('active').end().addClass('active');
            }
            var accountName = $.cookie('accountName');
            if (accountName !== undefined) accountNameField.val(accountName);
            $scope.setFocus();
        };
        $scope.addListeners = function () {
            $('#login-tabs').on('toggled', function () {
                $scope.setFocus();
            });
            // set up listener to capture and save values if remember checked
            $('#euca-login-form').on('submit', function () {
                isLogginIn = true;
                $.cookie('account', accountField.val(), {expires: 180});
                $.cookie('username', $('#username').val(), {expires: 180});
                $.cookie('login-form', 'eucalyptus', {expires: 180});
            });
            $('#aws-login-form').on('submit', function (evt) {
                $.cookie('login-form', 'aws', {expires: 180});
                // assemble request for aws type login
                // build params
                var params = "AWSAccessKeyId=" + $('#access_key').val();
                params = params + "&Action=GetSessionToken";
                params = params + "&DurationSeconds=" + $('#duration').val();
                params = params + "&SignatureMethod=HmacSHA256";
                params = params + "&SignatureVersion=2";
                params = params + "&Timestamp=" + encodeURIComponent(new Date().toISOString().substring(0, 19) + "Z");
                params = params + "&Version=2011-06-15";
                // sign request
                var string_to_sign = "POST\nsts.amazonaws.com\n/\n" + params;
                var hash = CryptoJS.HmacSHA256(string_to_sign, $('#secret_key').val());
                var signature = hash.toString(CryptoJS.enc.Base64);
                var encoded = encodeURIComponent(signature);
                var storedRegion = Modernizr.localstorage && localStorage.getItem('aws-region') || '';
                params = params + "&Signature=" + encoded;
                $('#aws_csrf_token').val($('#csrf_token').val());
                $('#package').val($.base64.encode(params));
                $('#aws-region').val(storedRegion);
                evt.preventDefault();
                $('#false-aws-login-form').submit();
            });
            accountField.on('keydown', $scope.eucaCheckValid);
            usernameField.on('keydown', $scope.eucaCheckValid);
            passwordField.on('keydown', $scope.eucaCheckValid);
            accessKeyField.on('keydown', $scope.awsCheckValid);
            secretKeyField.on('change', $scope.awsCheckValid);
            accountNameField.on('keydown', $scope.oidcCheckValid);
        };
        $scope.eucaCheckValid = function() {
            $timeout(function() {  // this causes an additional digest cycle after current thread completes
                $scope.eucaNotValid = $scope.eucaLoginNotValid();
            }, 100);
        };
        $scope.eucaLoginNotValid = function () {
            var account = accountField.val();
            var username = usernameField.val();
            var password = passwordField.val();
            if (!account || !username || !password) {
                return true;
            }
            return false;
        };
        $scope.awsCheckValid = function() {
            $timeout(function() {  // this causes an additional digest cycle after current thread completes
                $scope.awsNotValid = $scope.awsLoginNotValid();
            }, 200);
        };
        $scope.awsLoginNotValid = function () {
            var access_key = accessKeyField.val();
            var secret_key = secretKeyField.val();
            if (!access_key || !secret_key) {
                return true;
            }
            return false;
        };
        $scope.oidcCheckValid = function() {
            $timeout(function() {  // this causes an additional digest cycle after current thread completes
                $scope.oidcNotValid = $scope.oidcLoginNotValid();
            }, 100);
        };
        $scope.oidcLoginNotValid = function () {
            var account_name = accountNameField.val();
            if (!account_name) {
                return true;
            }
            return false;
        };
        $scope.openOIDCModal = function($event) {
            $event.preventDefault();
            $("#oidc-account-modal").foundation('reveal', 'open');
            $timeout(function() {
                accountNameField.focus();
                $scope.oidcCheckValid();
            }, 250);
        };
        $scope.handleOIDCLogin = function($event) {
            $event.preventDefault();
            $.cookie('accountName', accountNameField.val(), {expires: 180});
            window.location.href = $scope.oidcUrl + "-" + $('#account-name').val();
        };
    })
;
