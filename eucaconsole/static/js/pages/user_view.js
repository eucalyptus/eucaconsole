/*
 * @fileOverview user view page JS
 * @requires AngularJS
 *
 */


// user view page includes the User Editor editor
angular.module('UserView', ['PolicyList', 'Quotas', 'EucaConsoleUtils'])
    .controller('UserViewCtrl', function ($scope, $http, eucaUnescapeJson, handleError) {
        $scope.disable_url = '';
        $scope.allUsersRedirect = '';
        $scope.form = $('#user-update-form');
        $scope.ec2_expanded = false;
        $scope.s3_expanded = false;
        $scope.autoscale_expanded = false;
        $scope.elb_expanded = false;
        $scope.iam_expanded = false;
        $scope.currentTab = 'general-tab';
        $scope.isSubmitted = false;
        $scope.isNotChanged = true;
        $scope.pendingModalID = '';
        $scope.unsavedChangesWarningModalLeaveCallback = null;
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
        $scope.toggleTab = function (tab) {
            $(".tabs").children("dd").each(function() {
                var id = $(this).find("a").attr("href").substring(1);
                var $container = $("#" + id);
                $(this).removeClass("active");
                $container.removeClass("active");
                if (id == tab || $container.find("#" + tab).length) {
                    $(this).addClass("active");
                    $container.addClass("active");
                    $scope.currentTab = id; // Update the currentTab value for the help display
                    $scope.$broadcast('updatedTab', $scope.currentTab);
                }
             });
        };
        $scope.clickTab = function ($event, tab){
            $event.preventDefault();
            // If there exists unsaved changes, open the wanring modal instead
            if ($scope.isNotChanged === false) {
                $scope.openModalById('unsaved-changes-warning-modal');
                $scope.unsavedChangesWarningModalLeaveCallback = function() {
                    $scope.isNotChanged = true;
                    $scope.toggleTab(tab);
                    $('#unsaved-changes-warning-modal').foundation('reveal', 'close');
                };
                return;
            } 
            $scope.toggleTab(tab);
        };
        $scope.initController = function(optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.userName = options['user_name'];
            $scope.disable_url = options['user_disable_url'];
            $scope.allUsersRedirect = options['all_users_redirect'];
            $('#delete-user-form').attr('action', options['user_delete_url']);
            $scope.setFocus();
            $scope.setWatch();
            $scope.setDropdownMenusListener();
            $scope.adjustTab();
        };
        $scope.adjustTab = function() {
            var hash = $scope.currentTab;
            var matches = document.URL.match(/tab=([\w|-]+)/);
            if (matches != null && matches.length > 0) {
                if(matches[1] == 'general-tab' || matches[1] == 'security-tab' || matches[1] == 'quotas-tab'){
                    hash = matches[1];
                }
            }
            $scope.toggleTab(hash);
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
        $scope.setWatch = function() {
            // Monitor the action menu click
            $(document).on('click', 'a[id$="action"]', function (event) {
                // Ingore the action if the link has ng-click or href attribute defined
                if (this.getAttribute('ng-click')) {
                    return;
                } else if (this.getAttribute('href') && this.getAttribute('href') !== '#') {
                    return;
                }
                // the ID of the action link needs to match the modal name
                var modalID = this.getAttribute('id').replace("-action", "-modal");
                // If there exists unsaved changes, open the wanring modal instead
                if ($scope.isNotChanged === false) {
                    $scope.pendingModalID = modalID;
                    $scope.openModalById('unsaved-changes-warning-modal');
                    $scope.unsavedChangesWarningModalLeaveCallback = function() {
                        $scope.openModalById($scope.pendingModalID);
                    };
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
                $scope.unsavedChangesWarningModalLeaveCallback();
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
                }else if ($scope.isNotChanged === false) {
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
        $scope.setDropdownMenusListener = function () {
            var modals = $('[data-reveal]');
            modals.on('open', function () {
                $('.gridwrapper').find('.f-dropdown').filter('.open').css('display', 'none');
            });
            modals.on('close', function () {
                $('.gridwrapper').find('.f-dropdown').filter('.open').css('display', 'block');
            });
        };
        $scope.setFocus = function () {
            $(document).on('ready', function(){
                $('.tabs').find('a').get(0).focus();
            });
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var modalID = $(this).attr('id');
                if( modalID.match(/terminate/)  || modalID.match(/delete/) || modalID.match(/release/) ){
                    var closeMark = modal.find('.close-reveal-modal');
                    if(!!closeMark){
                        closeMark.focus();
                    }
                }else{
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
        $scope.disableUser = function ($event) {
            $event.preventDefault();
            var data = "csrf_token="+$('#csrf_token').val();
            $http({method:'POST', url:$scope.disable_url, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                // could put data back into form, but form already contains changes
                if (oData.error == undefined) {
                    Notify.success(oData.message);
                    window.location = $scope.allUsersRedirect;
                } else {
                    Notify.failure(oData.message);
                }
              }).
              error(function (oData, status) {
                handleError(oData, status);
              });
            $('#disable-user-modal').foundation('reveal', 'close');
        };
    })
    .controller('UserUpdateCtrl', function($scope) {
        $scope.isUserInfoNotChanged = true;
        $scope.initController = function () {
            $scope.setWatch();
        };
        $scope.setWatch = function () {
            $scope.$watch('isUserInfoNotChanged', function() {
                $scope.$parent.isNotChanged = $scope.isUserInfoNotChanged;
            });
            $scope.$on('updatedTab', function(event, tab) {
                if (tab === 'general-tab'){
                    $scope.$parent.isNotChanged = $scope.isUserInfoNotChanged;
                }
            }); 
            $(document).on('input', '#user-update-form input[type="text"]', function () {
                $scope.isUserInfoNotChanged = false;
                $scope.$apply();
            });
        };
    })
    .controller('UserPasswordCtrl', function($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.jsonRandomEndpoint = '';
        $scope.jsonDeleteEndpoint = '';
        $scope.jsonChangeEndpoint = '';
        $scope.getFileEndpoint = '';
        $scope.data = '';
        $scope.has_password = false;
        $scope.isPasswordNotChanged = true;
        $scope.initController = function (jsonRandomEndpoint, jsonDeleteEndpoint, jsonChangeEndpoint, getFileEndpoint, has_password) {
            $scope.jsonRandomEndpoint = jsonRandomEndpoint;
            $scope.jsonDeleteEndpoint = jsonDeleteEndpoint;
            $scope.jsonChangeEndpoint = jsonChangeEndpoint;
            $scope.getFileEndpoint = getFileEndpoint;
            $scope.has_password = has_password;
            var newPasswordForm = $('#new_password');
            // add password strength meter to first new password field
            newPasswordForm.after("<hr id='password-strength'/><span id='password-word'></span>");
            $('#password-strength').attr('class', "password_none");
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
            $("#change-password-modal").on('show', function () {
                $('#password').focus(); // doesn't seem to work.
            });
            $('#wrong-password').css('display', 'none');
            $scope.setWatch();
        };
        $scope.setWatch = function() { 
            $scope.$watch('isPasswordNotChanged', function() {
                $scope.$parent.isNotChanged = $scope.isPasswordNotChanged;
            });
            $scope.$on('updatedTab', function(event, tab) {
                if (tab === 'security-tab'){
                    $scope.$parent.isNotChanged = $scope.isPasswordNotChanged;
                }
            }); 
            $(document).on('input', '#user-change-password-form input[type="password"]', function () {
                $scope.isPasswordNotChanged = false;
                $scope.$apply();
            });
        };
        // Handles first step in submit.. validation and dialog
        $scope.submitChange = function($event) {
            $('#password-length').css('display', 'none');
            $('#passwords-match').css('display', 'none');
            var newpass = $event.target.new_password.value;
            var newpass2 = $event.target.new_password2.value;
            if (newpass.length < 6) {
                $('#password-length').css('display', 'block');
                return false;
            }
            if (newpass != newpass2) {
                $('#passwords-match').css('display', 'block');
                return false;
            }
            $scope.data = $($event.target).serialize();
            // open modal to get current password
            $('#password').val('');
            $('#change-password-modal').foundation('reveal', 'open');
        };
        // handles server call for changing the password
        $scope.changePassword = function($event) {
            $event.preventDefault();
            var form = $($event.target);
            var csrf_token = form.find('input[name="csrf_token"]').val();
            $('#wrong-password').css('display', 'none');
            // add in current password, then submit the request
            var data = $scope.data+"&password="+$event.target.password.value+"&csrf_token="+csrf_token;
            $http({method:'POST', url:$scope.jsonChangeEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                $('#change-password-modal').foundation('reveal', 'close');
                var results = oData ? oData.results : [];
                Notify.success(oData.message);
                $('#new_password').val("");
                $('#new_password2').val("");
                $('#password-strength').removeAttr('class');
                $('#password-word').text('');
                $scope.has_password = true;
                $.generateFile({
                    csrf_token: csrf_token,
                    filename: 'not-used', // let the server set this
                    content: 'none',
                    script: $scope.getFileEndpoint
                });
                $scope.isPasswordNotChanged = true;
            }).error(function (oData, status) {
                handleError(oData, status);
                $('#wrong-password').css('display', 'block');
            });
        };
        // handles server call for generating a random password
        $scope.genPassword = function($event) {
            var form = $($event.target);
            var csrf_token = $('#csrf_token').val();
            var data = "csrf_token="+csrf_token;
            $http({method:'POST', url:$scope.jsonRandomEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                Notify.success(oData.message);
                $scope.has_password = true;
                $.generateFile({
                    csrf_token: csrf_token,
                    filename: 'not-used', // let the server set this
                    content: 'none',
                    script: $scope.getFileEndpoint
                });
            }).error(function (oData, status) {
                handleError(oData, status);
            });
            $('#change-password-modal').foundation('reveal', 'close');
        };
        $scope.deletePassword = function($event) {
            $event.preventDefault();
            var form = $($event.target);
            var csrf_token = form.find('input[name="csrf_token"]').val();
            var data = $scope.data+"&csrf_token="+csrf_token;
            $http({method:'POST', url:$scope.jsonDeleteEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.has_password = false;
                Notify.success(oData.message);
            }).error(function (oData, status) {
                handleError(oData, status);
            });
            $('#delete-password-modal').foundation('reveal', 'close');
        };
    })
    .controller('UserAccessKeysCtrl', function($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.jsonEndpoint = '';
        $scope.jsonItemsEndpoint = '';
        $scope.getFileEndpoint = '';
        $scope.items = [];
        $scope.itemsLoading = true;
        $scope.userWithKey = '';
        $scope.keyToDelete = '';
        $scope.initController = function (jsonEndpoint, jsonItemsEndpoint, getFileEndpoint) {
            $scope.jsonEndpoint = jsonEndpoint;
            $scope.jsonItemsEndpoint = jsonItemsEndpoint;
            $scope.getFileEndpoint = getFileEndpoint;
            $scope.getItems(jsonItemsEndpoint);
        };
        $scope.getItems = function (jsonItemsEndpoint) {
            $http.get(jsonItemsEndpoint).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = false;
                $scope.items = results;
            }).error(function (oData, status) {
                handleError(oData, status);
            });
        };
        $scope.generateKeys = function ($event) {
            var form = $($event.target);
            var csrf_token = form.find('input[name="csrf_token"]').val();
            var data = "csrf_token="+csrf_token;
            $http({method:'POST', url:$scope.jsonEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                Notify.success(oData.message);
                $scope.itemsLoading = true;
                $scope.items = [];
                $scope.getItems($scope.jsonItemsEndpoint);
                $.generateFile({
                    csrf_token: csrf_token,
                    filename: 'not-used', // let the server set this
                    content: 'none',
                    script: $scope.getFileEndpoint
                });
            }).error(function (oData, status) {
                handleError(oData, status);
            });
        };
        $scope.makeAjaxCall = function (url, item) {
            url = url.replace("_name_", item['user_name']).replace("_key_", item['access_key_id']);
            var data = "csrf_token="+$('#csrf_token').val();
            $http({method:'POST', url:url, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = true;
                $scope.items = [];
                $scope.getItems($scope.jsonItemsEndpoint);
                Notify.success(oData.message);
              }).
              error(function (oData, status) {
                if (status == 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
                var errorMsg = oData['message'] || '';
                Notify.failure(errorMsg);
              });
        };
        $scope.confirmDelete = function (item) {
            var modal = $('#delete-key-modal');
            $scope.userWithKey = item.user_name;
            $scope.keyToDelete = item.access_key_id;
            modal.foundation('reveal', 'open');
        };
        $scope.deleteKey = function ($event, url) {
            $event.preventDefault();
            url = url.replace("_name_", $scope.userWithKey).replace("_key_", $scope.keyToDelete);
            var data = "csrf_token="+$('#csrf_token').val();
            $http({method:'POST', url:url, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = true;
                $scope.items = [];
                $scope.getItems($scope.jsonItemsEndpoint);
                Notify.success(oData.message);
              }).
              error(function (oData, status) {
                if (status == 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
                var errorMsg = oData['message'] || '';
                Notify.failure(errorMsg);
              });
            $('#delete-key-modal').foundation('reveal', 'close');
        };
    })
    // this directive allows for the watch function below that triggers a chosen:updated
    // event when the groupNames value in the scope is updated (by XHR). We can't simply
    // trigger the even from the XHR success function since angular hasn't updated the
    // ng-options yet.
    .directive('chosen', function () {
        var linker = function(scope, element, attr) {
            scope.$watch('groupNames', function() {
                element.trigger('chosen:updated');
            });
            element.chosen();
        };
        return {
            restrict:'A',
            link: linker
        }
    })
    .controller('UserGroupsCtrl', function($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.addEndpoint = '';
        $scope.removeEndpoint = '';
        $scope.jsonItemsEndpoint = '';
        $scope.jsonGroupsEndpoint = '';
        $scope.jsonGroupPoliciesEndpoint = '';
        $scope.jsonGroupPolicyEndpoint = '';
        $scope.groupName = '';
        $scope.isGroupNotSelected = true;
        $scope.groupNames = [];
        $scope.items = [];
        $scope.itemsLoading = true;
        $scope.policyName = '';
        $scope.policyJson = '';
        $scope.noAvailableGroups = false;
        $scope.alreadyMemberOfAllGroups = false;
        $scope.noGroupsDefined = false;
        $scope.initController = function (addEndpoint, removeEndpoint, jsonItemsEndpoint, jsonGroupsEndpoint,
                                          jsonGroupPoliciesEndpoint, jsonGroupPolicyEndpoint, alreadyMemberText, noGroupsDefinedText) {
            $scope.addEndpoint = addEndpoint;
            $scope.removeEndpoint = removeEndpoint;
            $scope.jsonItemsEndpoint = jsonItemsEndpoint;
            $scope.jsonGroupsEndpoint = jsonGroupsEndpoint;
            $scope.jsonGroupPoliciesEndpoint = jsonGroupPoliciesEndpoint;
            $scope.jsonGroupPolicyEndpoint = jsonGroupPolicyEndpoint;
            $scope.alreadyMemberText = alreadyMemberText;
            $scope.noGroupsDefinedText = noGroupsDefinedText;
            $scope.getItems(jsonItemsEndpoint);
            $scope.getAvailableGroups();
            $scope.setWatcher();
        };
        $scope.setWatcher = function () {
            $scope.$watch('groupName', function () {
                if ($scope.groupName === '') {
                    $scope.isGroupNotSelected = true;
                } else {
                    $scope.isGroupNotSelected = false;
                }
            });
        };
        $scope.getItems = function (jsonItemsEndpoint) {
            $http.get(jsonItemsEndpoint).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = false;
                $scope.items = results;
                for (var i=0; i<results.length; i++) {
                    $scope.loadPolicies(results[i].group_name, i);
                }
            }).error(function (oData, status) {
                handleError(oData, status);
            });
        };
        $scope.loadPolicies = function (groupName, index) {
            var url = $scope.jsonGroupPoliciesEndpoint.replace('_name_', groupName);
            $http.get(url).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.items[index].policies = results;
            }).error(function (oData, status) {
                handleError(oData, status);
            });
        };
        $scope.getAvailableGroups = function () {
            $http.get($scope.jsonGroupsEndpoint).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.groupNames = results;
                $scope.alreadyMemberOfAllGroups = results.indexOf($scope.alreadyMemberText) !== -1;
                $scope.noGroupsDefined = results.indexOf($scope.noGroupsDefinedText) !== -1;
                $scope.noAvailableGroups = $scope.alreadyMemberOfAllGroups || $scope.noGroupsDefined;
                $scope.groupName = '';
            }).error(function (oData, status) {
                handleError(oData, status);
            });
        };
        $scope.addUserToGroup = function ($event) {
            var group_name = $scope.groupName;
            var url = $scope.addEndpoint.replace("_group_", group_name);
            var data = "csrf_token="+$('#csrf_token').val();
            $http({method:'POST', url:url, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = true;
                $scope.items = [];
                $scope.getItems($scope.jsonItemsEndpoint);
                $scope.getAvailableGroups();
                Notify.success(oData.message);
              }).
              error(function (oData, status) {
                var errorMsg = oData['message'] || '';
                Notify.failure(errorMsg);
              });
        };
        $scope.removeUserFromGroup = function (item) {
            var group_name = item.group_name;
            var url = $scope.removeEndpoint.replace("_group_", group_name);
            var data = "csrf_token="+$('#csrf_token').val();
            $http({method:'POST', url:url, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = true;
                $scope.items = [];
                $scope.getItems($scope.jsonItemsEndpoint);
                $scope.getAvailableGroups();
                Notify.success(oData.message);
              }).
              error(function (oData, status) {
                var errorMsg = oData['message'] || '';
                Notify.failure(errorMsg);
              });
        };
        $scope.showPolicy = function ($event, groupName, policyName) {
            $event.preventDefault();
            $scope.policyJson = ''; // clear any previous policy
            $scope.policyName = policyName
            var url = $scope.jsonGroupPolicyEndpoint.replace('_name_', groupName).replace('_policy_', policyName);
            $http.get(url).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.policyJson = results;
            }).error(function (oData, status) {
                handleError(oData, status);
            });
            $('#policy-view-modal').foundation('reveal', 'open');
        };
    })
    .controller('UserQuotasCtrl', function($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.jsonEndpoint = '';
        $scope.isQuotaNotChanged = true;
        $scope.initController = function (jsonEndpoint) {
            $scope.jsonEndpoint = jsonEndpoint;
            $scope.setWatch();
        };
        $scope.setWatch = function () {
            $scope.$watch('isQuotaNotChanged', function() {
                $scope.$parent.isNotChanged = $scope.isQuotaNotChanged;
            });
            $scope.$on('updatedTab', function(event, tab) {
                if (tab === 'quotas-tab'){
                    $scope.$parent.isNotChanged = $scope.isQuotaNotChanged;
                }
            }); 
            $(document).on('input', '#quotas-panel input[type="text"]', function () {
                $scope.isQuotaNotChanged = false;
                $scope.$apply();
            });
        };
        $scope.submit = function($event) {
            $('#quota-error').css('display', 'none');
            var invalid = $($event.target).find('input[data-invalid]');
            if (invalid.length > 0) {
                $('#quota-error').css('display', 'block');
                return false;
            }
            var data = $($event.target).serialize();
            $http({method:'POST', url:$scope.jsonEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                Notify.success(oData.message);
                $scope.isQuotaNotChanged = true;
              }).
              error(function (oData, status) {
                var errorMsg = oData['message'] || '';
                Notify.failure(errorMsg);
              });
        };
    })
;

