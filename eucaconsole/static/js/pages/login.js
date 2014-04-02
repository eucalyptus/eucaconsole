
/**
 * @fileOverview Login page JS
 * @requires AngularJS
 *
 */

angular.module('LoginPage', [])
    .controller('LoginPageCtrl', function ($scope) {
        $scope.initController = function () {
            $('#javascript-warning').css('display', 'none');
            $scope.prefillForms();
            $scope.addListeners();
            /* old-style browser version detection... modernizr instead?
            var supportedBrowser = false;
            if ($.browser.mozilla && parseInt($.browser.version, 10) > 24) {
                 supportedBrowser = true;
            } else if (Object.hasOwnProperty.call(window, "ActiveXObject") && !window.ActiveXObject && parseInt($.browser.version, 10) > 9) {
                 // this test is for IE 
                 supportedBrowser = true;
            } else if ($.browser.webkit) {
                userAgent = navigator.userAgent.toLowerCase();
                rwebkit = new RegExp("webkit/([0-9]+)");
                res = rwebkit.exec(userAgent);
                if (res && res[1] > 535) {
                    supportedBrowser = true;
                }
            }
            if (!supportedBrowser) {
                $('#browser-version-modal').foundation('reveal', 'open');
            }
            */
            if (window.location.protocol != 'https:') {
                $('#ssl-off-modal').foundation('reveal', 'open');
            }
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
        $scope.prefillForms = function () {
            // pre-fill if cookies are present
            var account = $.cookie('account');
            if (account !== undefined) $('#account').val(account);

            var last_login = $.cookie('login-form');
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
                params = params + "&Signature=" + encoded;
                $('#aws_csrf_token').val($('#csrf_token').val());
                $('#package').val($.base64.encode(params));
                $('#aws-region').val(localStorage.getItem('aws-region'));
                evt.preventDefault();
                $('#false-aws-login-form').submit();
            });
        };
    })
;
