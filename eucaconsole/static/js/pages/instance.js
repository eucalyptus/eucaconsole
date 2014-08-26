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
        $scope.pendingModalID = '';
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
        $scope.createImageClicked = function (running_create, instance_id) {
            $('.actions-menu').trigger('click');
            if (running_create) {
                $scope.instanceID = instance_id;
                var modal = $('#create-image-denied-modal');
                modal.foundation('reveal', 'open');
            }
            else {
                window.location = '/instances/' + instance_id + '/createimage';
            }
        }
        $scope.revealConsoleOutputModal = function() {
            $('.actions-menu').trigger('click');
            $http.get($scope.consoleOutputEndpoint).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $scope.consoleOutput = $.base64.decode(results);
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
        $scope.openModalById = function (modalID) {
            var modal = $('#' + modalID);
            modal.foundation('reveal', 'open');
            modal.find('h3').click();  // Workaround for dropdown menu not closing
            // Clear the pending modal ID if opened
            if ($scope.pendingModalID === modalID) {
                $scope.pendingModalID = '';
            }
        };
        $scope.setWatch = function () {
            // Monitor the action menu click
            $(document).on('click', 'a[id$="action"]', function (event) {
                // Ingore the action if the link has ng-click or href attribute defined
                if (this.getAttribute('ng-click')) {
                    return;
                } else if (this.getAttribute('href') !== '#') {
                    return;
                }
                // the ID of the action link needs to match the modal name
                var modalID = this.getAttribute('id').replace("-action", "-modal");
                // If there exists unsaved changes, open the wanring modal instead
                // Exception of 'connect-instance-modal', which doesn't leave the page
                if (modalID !== 'connect-instance-modal' && ($scope.existsUnsavedTag() || $scope.isNotChanged === false)) {
                    $scope.pendingModalID = modalID;
                    $scope.openModalById('unsaved-changes-warning-modal');
                    return;
                } 
                $scope.openModalById(modalID);
            });
            // Leave button is clicked on the warning unsaved changes modal
            $(document).on('click', '#unsaved-changes-warning-modal-stay-button', function () {
                $('#unsaved-changes-warning-modal').foundation('reveal', 'close');
            });
            // Stay button is clicked on the warning unsaved changes modal
            $(document).on('click', '#unsaved-changes-warning-modal-leave-link', function () {
                $scope.openModalById($scope.pendingModalID);
            });
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
            // Conditions to check before navigate away
            window.onbeforeunload = function(event) {
                if ($scope.isSubmitted === true) {
                   // The action is "submit". OK to proceed
                   return;
                }else if ($scope.existsUnsavedTag() || $scope.isNotChanged === false) {
                    // Warn the user about the unsaved changes
                    return $('#warning-message-unsaved-changes').text();
                }
                return;
            };
            // Do not perfom the unsaved changes check if the cancel link is clicked
            $(document).on('click', '.cancel-link', function(event) {
                window.onbeforeunload = null;
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
                $scope.isSubmitted = false;
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

