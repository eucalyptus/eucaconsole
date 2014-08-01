/**
 * @fileOverview Instance page JS
 * @requires AngularJS
 *
 */

// Instance page includes the tag editor, so pull in that module as well.
angular.module('InstancePage', ['TagEditor'])
    .controller('InstancePageCtrl', function ($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.instanceStateEndpoint = '';
        $scope.instanceUserDataEndpoint = '';
        // Valid instance states are: "pending", "running", "shutting-down", "terminated", "stopping", "stopped"
        // 'shutting-down' = terminating state
        $scope.transitionalStates = ['pending', 'stopping', 'shutting-down'];
        $scope.instanceState = '';
        $scope.isFileUserData = false;
        $scope.isNotChanged = true;
        $scope.isSubmitted = false;
        $scope.isUpdating = false;
        $scope.isNotStopped = $scope.instanceState != 'stopped';
        $scope.instanceForm = $('#instance-form');
        $scope.isTransitional = function (state) {
            return $scope.transitionalStates.indexOf(state) !== -1;
        };
        $scope.initController = function (jsonEndpoint, userDataEndpoint, ipaddressEndpoint, consoleEndpoint, state, id, public_ip, public_dns_name, platform, has_elastic_ip) {
            $scope.instanceStateEndpoint = jsonEndpoint;
            $scope.instanceUserDataEndpoint = userDataEndpoint;
            $scope.instanceIPAddressEndpoint = ipaddressEndpoint;
            $scope.consoleOutputEndpoint = consoleEndpoint;
            $scope.instanceState = state;
            $scope.instanceID = id;
            $scope.instancePublicIP = public_ip;
            $scope.publicDNS = public_dns_name;
            $scope.platform = platform;
            $scope.hasElasticIP = Boolean(has_elastic_ip.toLowerCase());
            $scope.getInstanceState();
            $scope.getUserData();
            $scope.activateWidget();
            $scope.setWatch();
            $scope.setFocus();
            $('#file').on('change', $scope.getPassword);
        };
        $scope.activateWidget = function () {
            $('#associate-ip-to-instance-modal').on('open', function(){
                var thisSelect = $(this).find('#ip_address');
                thisSelect.chosen({'width': '80%', 'search_contains': true});
            });
        };
        $scope.revealConsoleOutputModal = function() {
            $('.actions-menu').trigger('click');
            $http.get($scope.consoleOutputEndpoint).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $scope.consoleOutput = results;
                    var modal = $('#console-output-modal');
                    modal.foundation('reveal', 'open');
                }
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
            });
        };
        $scope.setFocus = function () {
            $(document).on('ready', function(){
                $('.tabs').find('a').get(0).focus();
            });
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var modalID = $(this).attr('id');
                if (modalID.match(/terminate/) || modalID.match(/delete/) || 
                    modalID.match(/release/) || modalID.match(/reboot/)) {
                    var closeMark = modal.find('.close-reveal-modal');
                    if (!!closeMark) {
                        closeMark.focus();
                    }
                } else {
                    var inputElement = modal.find('input[type!=hidden]').get(0);
                    var modalButton = modal.find('button').get(0);
                    if (!!inputElement) {
                        inputElement.focus();
                    } else if (!!modalButton) {
                        modalButton.focus();
                    }
               }
            });
        };
        // True if there exists an unsaved key or value in the tag editor field
        $scope.existsUnsavedTag = function () {
            var hasUnsavedTag = false;
            $('input.taginput[type!="checkbox"]').each(function(){
                if ($(this).val() !== '') {
                    hasUnsavedTag = true;
                }
            });
            return hasUnsavedTag;
        };
        $scope.setWatch = function () {
            $scope.$on('tagUpdate', function($event) {
                $scope.isNotChanged = false;
            });
            $(document).on('input', 'input[type="text"]', function () {
                $scope.isNotChanged = false;
                $scope.$apply();
            });
            $(document).on('input', 'textarea', function () {  // userdata text
                $scope.intputtype = 'text';
                $scope.isNotChanged = false;
                $scope.$apply();
            });
            $('#userdata_file').on('change', function () {  // userdata file
                $scope.intputtype = 'file';
                $scope.isNotChanged = false;
                $scope.$apply();
            });
            $(document).on('change', 'select', function () {
                $scope.isNotChanged = false;
                $scope.$apply();
            });
            $scope.$watch('instanceState', function(){
                $scope.getIPAddressData();
            });
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
            });
            // Turn "isSubmiited" flag to true when a submit button is clicked on the page
            $('form[id!="euca-logout-form"]').on('submit', function () {
                $scope.isSubmitted = true;
            });
            window.onbeforeunload = function(event) {
                // Conditions to check before navigate away from the page
                // Either by "Submit" or clicking links on the page
                if ($scope.existsUnsavedTag()) {
                    // In case of any unsaved tags, warn the user before unloading the page
                    return $('#warning-message-unsaved-tag').text();
                } else if ($scope.isNotChanged === false) {
                    // No unsaved tags, but some input fields have been modified on the page
                    if ($scope.isSubmitted === true) {
                        // The action is "submit". OK to proceed
                        return;
                    } else {
                        // The action is navigate away.  Warn the user about the unsaved changes
                        return $('#warning-message-unsaved-change').text();
                    }
                }
            };
            // Do not perfom the unsaved changes check if the cancel link is clicked
            $(document).on('click', '.cancel-link', function(event) {
                window.onbeforeunload = null;
            });
            // Handle the case when user tries to open a dialog while there exist unsaved changes
            $(document).on('open', '[data-reveal][id!="unsaved-changes-warning-modal"][id!="unsaved-tag-warn-modal"]', function () {
                // If there exist unsaved changes
                if ($scope.existsUnsavedTag() || $scope.isNotChanged === false) {
                    var self = this;
                    // Close the current dialog as soon as it opens
                    $(self).on('opened', function() {
                        $(self).off('opened');
                        $(self).foundation('reveal', 'close');
                    });
                    // Open the warning message dialog instead
                    $(self).on('closed', function() {
                        $(self).off('closed');
                        var modal = $('#unsaved-changes-warning-modal');
                        modal.foundation('reveal', 'open');
                    });
                } 
            });
        };
        $scope.getIPAddressData = function () {
            $http.get($scope.instanceIPAddressEndpoint).success(function(oData) {
                $scope.instancePublicIP = oData ? oData.ip_address : '';
                $scope.PublicDNS = oData ? oData.public_dns_name : '';
                $scope.instancePrivateIP = oData ? oData.private_ip_address : '';
                $scope.PrivateDNS = oData ? oData.private_dns_name : '';
                $scope.hasElasticIP = oData ? oData.has_elastic_ip : '';
            });
        };
        $scope.getInstanceState = function () {
            $http.get($scope.instanceStateEndpoint).success(function(oData) {
                $scope.instanceState = oData ? oData.results : '';

                // Poll to obtain desired end state if current state is transitional
                if ($scope.isTransitional($scope.instanceState)) {
                    $scope.isUpdating = true;
                    $timeout(function() {$scope.getInstanceState()}, 4000);  // Poll every 4 seconds
                } else {
                    $scope.isUpdating = false;
                }
                $scope.isNotStopped = $scope.instanceState != 'stopped';
            });
        };
        $scope.getUserData = function () {
            $http.get($scope.instanceUserDataEndpoint).success(function(oData) {
                var userData = oData ? oData.results : '';
                if (userData.type.indexOf('text') === 0) {
                    $scope.isFileUserData = false;
                    $("#userdata:not([display='none'])").val(userData.data);
                    $timeout(function() { $scope.inputtype = 'text'; });
                }
                else {
                    $scope.isFileUserData = true;
                    $("#userdatatype:not([display='none'])").text(userData.type);
                    $timeout(function() { $scope.inputtype = 'file'; });
                }
            });
        };
        $scope.submitSaveChanges = function($event){
            // Handle the unsaved tag issue
            var existsUnsavedTag = false;
            $('input.taginput').each(function(){
                if ($(this).val() !== '') {
                    existsUnsavedTag = true;
                    return false;
                }
            });
            if (existsUnsavedTag) {
                $event.preventDefault();
                $('#unsaved-tag-warn-modal').foundation('reveal', 'open');
            } else if ($scope.instanceState == 'stopped') {
                $event.preventDefault();
                $('#update-instance-modal').foundation('reveal', 'open');
            }
        };
        $scope.submitUpdateInstance = function ($event) {
            $event.preventDefault();
            $('a.close-reveal-modal').trigger('click');
            $('#start_later').val('true');
            $scope.instanceForm.submit();
        };
        $scope.cancelUpdateInstance = function ($event) {
            $event.preventDefault();
            $('a.close-reveal-modal').trigger('click');
            $scope.instanceForm.submit();
        };
        $scope.promptFile = function (url) {
            $('#file').trigger('click');
            $scope.password_url = url;
        };
        $scope.getPassword = function (evt) {
            $('#file').attr('display', 'none');
            var file = evt.target.files[0];
            var reader = new FileReader();
            reader.onloadend = function(evt) {
                if (evt.target.readyState == FileReader.DONE) {
                    var key_contents = evt.target.result;
                    var url = $scope.password_url.replace("_id_", $scope.instanceID);
                    var data = "csrf_token=" + $('#csrf_token').val() + "&key=" + $.base64.encode(key_contents);
                    $http({method:'POST', url:url, data:data,
                           headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                      success(function(oData) {
                        var results = oData ? oData.results : [];
                        $('#the-password').text(results.password);
                      }).
                      error(function (oData, status) {
                        if (status == 403) window.location = '/';
                        var errorMsg = oData['message'] || '';
                        Notify.failure(errorMsg);
                      });
                }
            }
            reader.readAsText(file);
        }
    })
;

