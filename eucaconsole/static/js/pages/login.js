
/**
 * @fileOverview Login page JS
 * @requires AngularJS
 *
 */

angular.module('LoginPage', ['EucaConsoleUtils'])
    .controller('LoginPageCtrl', function ($scope, $timeout, eucaUnescapeJson) {
        $scope.showHttpsWarning = false;
        $scope.initController = function (json_options) {
            var options = JSON.parse(eucaUnescapeJson(json_options));
            $scope.prefillForms(options['account'], options['username']);
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
            Modernizr.sessionstorage && sessionStorage.removeItem('copy-object-buffer');
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
            if (account !== undefined) $('#account').val(account);
            if (username !== undefined) $('#username').val(username);

            if (last_login == 'aws') {  // select that tab
                // all this mimics what happens in the tab code itself... no other way I found worked.
                var tab = $('#aws-tab');
                tab.addClass('active').trigger('opened');
                tab.siblings().removeClass('active');
                var target = $('#aws');
                target.siblings().removeClass('active').end().addClass('active');
            }
            $scope.setFocus();
        };
        $scope.addListeners = function () {
            $('#login-tabs').on('toggled', function () {
                $scope.setFocus();
            });
            // set up listener to capture and save values if remember checked
            $('#euca-login-form').on('submit', function () {
                $.cookie('account', $('#account').val(), {expires: 180});
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
                //params = params+"&Timestamp="+"2014-01-16T19%3A36%3A32Z";
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
        };
    })
;
