/*
 * @fileOverview user view page JS
 * @requires AngularJS
 *
 */


// user view page includes the User Editor editor
angular.module('UserView', ['PolicyList'])
    .controller('UserViewCtrl', function ($scope, $http) {
        $scope.disable_url = '';
        $scope.allUsersRedirect = '';
        $scope.form = $('#user-update-form');
        $scope.ec2_expanded = false;
        $scope.s3_expanded = false;
        $scope.autoscale_expanded = false;
        $scope.elb_expanded = false;
        $scope.iam_expanded = false;
        $scope.currentTab = 'general-tab';
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
        $scope.clickTab = function ($event, tab){
           $scope.currentTab = tab; 
           $event.preventDefault();
        };
        $scope.initController = function(user_name, disable_url, allRedirect, delete_url) {
            $scope.userName = user_name;
            $scope.disable_url = disable_url;
            $scope.allUsersRedirect = allRedirect;
            $('#delete-user-form').attr('action', delete_url);
            $scope.setFocus();
            $scope.setDropdownMenusListener();
            $scope.adjustTab();
        };
        $scope.adjustTab = function() {
            var hash = $scope.currentTab;
            var matches = document.URL.match(/tab=([\w|-]+)/);
            if (matches.length > 0) {
                hash = matches[1];
            }
            $(".tabs").children("dd").each(function() {
                var id = $(this).find("a").attr("href").substring(1);
                var $container = $("#" + id);
                $(this).removeClass("active");
                $container.removeClass("active");
                if (id == hash || $container.find("#" + hash).length) {
                    $(this).addClass("active");
                    $container.addClass("active");
                    $scope.currentTab = id;    // Update the currentTab value for the help display
                }
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
                var errorMsg = oData['message'] || '';
                Notify.failure(errorMsg);
              });
            $('#disable-user-modal').foundation('reveal', 'close');
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
                if (oData.error == undefined) {
                    Notify.success(oData.message);
                } else {
                    Notify.failure(oData.message);
                }
              }).
              error(function (oData, status) {
                var errorMsg = oData['message'] || '';
                Notify.failure(errorMsg);
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
            $('#change-password-modal').foundation('reveal', 'open');
        };
        // handles server call for changing the password
        $scope.changePassword = function($event) {
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
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || '';
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
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
                var errorMsg = oData['message'] || '';
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
                Notify.failure(errorMsg);
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
                var errorMsg = oData['message'] || '';
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
                Notify.failure(errorMsg);
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
                var errorMsg = oData['message'] || '';
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
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
                var errorMsg = oData['message'] || '';
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
                Notify.failure(errorMsg);
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
                var errorMsg = oData['message'] || '';
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
            });
        };
        $scope.loadPolicies = function (groupName, index) {
            var url = $scope.jsonGroupPoliciesEndpoint.replace('_name_', groupName);
            $http.get(url).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.items[index].policies = results;
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || '';
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
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
                var errorMsg = oData['message'] || '';
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
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
                var errorMsg = oData['message'] || '';
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
            });
            $('#policy-view-modal').foundation('reveal', 'open');
        };
    })
    .controller('UserQuotasCtrl', function($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.jsonEndpoint = '';
        $scope.initController = function (jsonEndpoint) {
            $scope.jsonEndpoint = jsonEndpoint;
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
              }).
              error(function (oData, status) {
                var errorMsg = oData['message'] || '';
                Notify.failure(errorMsg);
              });
        };
    })
;

