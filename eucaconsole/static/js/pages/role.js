/**
 * @fileOverview IAM Role Detail Page JS
 * @requires AngularJS
 *
 */

angular.module('RolePage', ['PolicyList', 'EucaConsoleUtils'])
    .controller('RolePageCtrl', function ($scope, $http, $timeout, eucaHandleError) {
        $scope.allUsers = [];
        $scope.trustPolicy = '';
        $scope.trustedEntity = '';
        $scope.codeEditor = null;
        $scope.editPolicyModal = $('#trust-policy-edit-modal');
        $scope.initController = function (all_users, trust_policy, trusted_entity) {
            $scope.allUsers = all_users;
            $scope.trustPolicy = trust_policy;
            $scope.trustedEntity = trusted_entity;
            $scope.setWatch();
            $scope.setFocus();
            $scope.initCodeMirror();
        };
        $scope.initCodeMirror = function () {
            var policyTextarea = document.getElementById('trust-policy-area');
            $scope.codeEditor = CodeMirror.fromTextArea(policyTextarea, {
                mode: {name:"javascript", json:true},
                lineWrapping: true,
                styleActiveLine: true,
                lineNumbers: true
            });
        };
        $scope.editPolicy = function ($event) {
            $event.preventDefault();
            $scope.editPolicyModal.foundation('reveal', 'open');
            $timeout(function() {
                $scope.codeEditor.setValue($scope.trustPolicy);
                $scope.codeEditor.focus();
            }, 1000);
        };
        $scope.saveTrustPolicy = function ($event, url) {
            $event.preventDefault();
            try {
                $('#trust-json-error').css('display', 'none');
                var policy_json = $scope.codeEditor.getValue();
                //var policy_json = $('#policy-area').val();
                JSON.parse(policy_json);
                $('#trust-policy-edit-modal').foundation('reveal', 'close');
                // now, save the policy
                var data = "csrf_token="+$('#csrf_token').val()+"&policy_text="+policy_json;
                $http({
                    method:'POST', url:url, data:data,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}}
                ).success(function(oData) {
                    $scope.trustPolicy = policy_json;
                    $scope.trustedEntity = oData.trusted_entity;
                    Notify.success(oData.message);
                }).error(function (oData, status) {
                    eucaHandleError(oData, status);
                });
            } catch (e) {
                $('#trust-json-error').text(e);
                $('#trust-json-error').css('display', 'block');
            }
        };
        $scope.setWatch = function () {
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
            });
        };
        $scope.setFocus = function () {
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
    })
;



