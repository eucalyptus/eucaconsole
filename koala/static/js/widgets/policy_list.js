/**
 * @fileOverview Policy List JS
 * @requires AngularJS
 *
 */
angular.module('PolicyList', [])
    .controller('PolicyListCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.policyList = $('#policy-list');
        $scope.itemsLoading = true;
        $scope.policyTextarea = $scope.policyList.find('textarea#policies');
        $scope.policiesUrl = '';
        $scope.policyUrl = '';
        $scope.removeUrl = '';
        $scope.updateUrl = '';
        $scope.policyArray = [];
        $scope.policyIndex = -1;
        $scope.policyName = '';
        $scope.policyJson = '';
        $scope.codeEditor = null;
        $scope.editPolicyArea = null;
        $scope.editPolicyModal = $('#policy-edit-modal');
        $scope.syncPolicies = function () {
            var policyObj = {};
            $scope.policyArray.forEach(function(policy) {
                policyObj[policy.name] = "nothing";
            });
            $scope.policyTextarea.val(JSON.stringify(policyObj));
        };
        $scope.initPolicies = function(policies_url, policy_url, remove_url, update_url) {
            $scope.policiesUrl = policies_url;
            $scope.policyUrl = policy_url;
            $scope.removeUrl = remove_url;
            $scope.updateUrl = update_url;
            $scope.initCodeMirror();
            $scope.getPolicies();
        };
        $scope.getPolicies = function () {
            $http({
                method:'GET', url:$scope.policiesUrl, data:'',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}}
            ).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = false;
                for (var i=0; i<results.length; i++) {
                    $scope.policyArray.push({
                        'name': results[i]
                    });
                }
                $scope.syncPolicies();
              }
            ).error(function (oData, status) {
                var errorMsg = oData['message'] || '';
                Notify.failure(errorMsg);
            });
        };
        $scope.removePolicy = function (index, $event) {
            $event.preventDefault();
            $scope.policyIndex = index;
            $scope.policyName = $scope.policyArray[index].name;
            $('#delete-modal').foundation('reveal', 'open');
        };
        $scope.initCodeMirror = function () {
            var policyTextarea = document.getElementById('policy-area');
            $scope.codeEditor = CodeMirror.fromTextArea(policyTextarea, {
                mode: {name:"javascript", json:true},
                lineWrapping: true,
                styleActiveLine: true,
                lineNumbers: true
            });
        };
        $scope.doDelete = function ($event) {
            $event.preventDefault();
            var url = $scope.removeUrl.replace('_policy_', $scope.policyName);
            var data = "csrf_token="+$('#csrf_token').val();
            $http({method:'POST', url:url, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}
            ).success(function(oData) {
                $scope.policyArray.splice($scope.policyIndex, 1);
                $scope.syncPolicies();
                Notify.success(oData.message);
            }).error(function (oData) {
                var errorMsg = oData['message'] || '';
                Notify.failure(errorMsg);
            });
            $('#delete-modal').foundation('reveal', 'close');
        };
        $scope.clearCodeEditor = function () {
            $scope.codeEditor.setValue('');
            $scope.codeEditor.clearHistory();
        };
        $scope.editPolicy = function (index, $event) {
            $event.preventDefault();
            $scope.clearCodeEditor();
            $scope.editPolicyModal.foundation('reveal', 'open');
            $scope.editPolicyModal.on('close', function() {
                $scope.clearCodeEditor();
            });
            $scope.policyJson = ''; // clear any previous policy
            $scope.policyName = $scope.policyArray[index].name;
            var url = $scope.policyUrl.replace('_policy_', $scope.policyName);
            $http.get(url).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.policyJson = results;
                $scope.codeEditor.setValue(results);
                $scope.codeEditor.focus();
            }).error(function (oData, status) {
                var errorMsg = oData['error'] || '';
                if (errorMsg && status === 403) {
                    $('#euca-logout-form').submit();
                }
            });
        };
        $scope.savePolicy = function($event) {
            $event.preventDefault();
            try {
                $('#json-error').css('display', 'none');
                var policy_json = $scope.codeEditor.getValue();
                //var policy_json = $('#policy-area').val();
                JSON.parse(policy_json);
                $('#policy-edit-modal').foundation('reveal', 'close');
                // now, save the policy
                var url = $scope.updateUrl.replace('_policy_', $scope.policyName);
                var data = "csrf_token="+$('#csrf_token').val()+"&policy_text="+policy_json;
                $http({
                    method:'POST', url:url, data:data,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}}
                ).success(function(oData) {
                    Notify.success(oData.message);
                }).error(function (oData) {
                    var errorMsg = oData['message'] || '';
                    Notify.failure(errorMsg);
                });
            } catch (e) {
                $('#json-error').text(e);
                $('#json-error').css('display', 'block');
            }
        };
    })
;
