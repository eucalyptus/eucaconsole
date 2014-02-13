/**
 * @fileOverview IAM Policy Wizard JS
 * @requires AngularJS
 *
 */

angular.module('IAMPolicyWizard', [])
    .controller('IAMPolicyWizardCtrl', function ($scope, $http) {
        $scope.wizardForm = $('#iam-policy-form');
        $scope.policyJsonEndpoint = '';
        $scope.policyTextarea = document.getElementById('policy');
        $scope.codeEditor = null;
        $scope.policyActions = {};
        $scope.initController = function (policyJsonEndpoint) {
            $scope.policyJsonEndpoint = policyJsonEndpoint;
            console.log($scope.policyActions)
            $scope.initCodeMirror();
        };
        $scope.initCodeMirror = function () {
            $scope.codeEditor = CodeMirror.fromTextArea($scope.policyTextarea, {
                mode: "javascript",
                lineWrapping: true,
                styleActiveLine: true,
                lineNumbers: true
            });
        };
        $scope.visitStep = function(step) {
            $('#tabStep' + step).click();
        };
        $scope.setPolicyName = function (policyType) {
            var typeNameMapping = {
                'admin_access': 'AccountAdminAccessPolicy',
                'user_access': 'PowerUserAccessPolicy',
                'monitor_access': 'ReadOnlyUserAccessPolicy',
                'blank': 'CustomAccessPolicy'
            }
            $scope.policyName = typeNameMapping[policyType] || '';
        };
        $scope.selectPolicy = function(policyType) {
            // Fetch hard-coded canned policies
            var jsonUrl = $scope.policyJsonEndpoint + "?type=" + policyType;
            $http.get(jsonUrl).success(function(oData) {
                var results = oData ? oData['policy'] : '',
                    formattedResults = '';
                if (results) {
                    formattedResults = JSON.stringify(results, null, 2);
                    $scope.policyText = formattedResults;
                    $scope.codeEditor.setValue(formattedResults);
                    $scope.codeEditor.focus();
                }
            });
            // Set policy name
            $scope.setPolicyName(policyType);
        };
    })
;

