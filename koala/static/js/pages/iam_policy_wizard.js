/**
 * @fileOverview IAM Policy Wizard JS
 * @requires AngularJS
 *
 */

angular.module('IAMPolicyWizard', [])
    .controller('IAMPolicyWizardCtrl', function ($scope, $http) {
        $scope.wizardForm = $('#iam-policy-form');
        $scope.policyGenerator = $('#policy-generator');
        $scope.policyJsonEndpoint = '';
        $scope.policyTextarea = document.getElementById('policy');
        $scope.codeEditor = null;
        $scope.policyStatements = [];
        $scope.addedStatements = [];
        $scope.policyAPIVersion = "2012-10-17";
        $scope.generatorPolicy = { "Version": $scope.policyAPIVersion, "Statement": $scope.policyStatements };
        $scope.initController = function (policyJsonEndpoint) {
            $scope.policyJsonEndpoint = policyJsonEndpoint;
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
        // Updates from policy generator
        $scope.updatePolicy = function () {
            var formattedResults = JSON.stringify($scope.generatorPolicy, null, 2);
            $scope.policyText = formattedResults;
            $scope.codeEditor.setValue(formattedResults);
        };
        // Add "Allow" or "Deny" statement
        $scope.addStatement = function (effect, namespace, action, $event) {
            var nsAction = namespace.toLowerCase() + ':' + action;
            var flattenedStatement =  effect + namespace + action;
            var tgt = $($event.target);
            var statement = {
                "Action": [nsAction],
                "Resource": "*",
                "Effect": effect  // Can be "Allow" or "Deny"
            };
            if ($scope.addedStatements.indexOf(flattenedStatement) === -1) {
                $scope.policyStatements.push(statement);
                $scope.addedStatements.push(flattenedStatement);
                $scope.updatePolicy();
            }
            tgt.closest('tr').find('i').removeClass('selected');
            tgt.addClass('selected');
        };
        $scope.toggleAll = function (action, namespace, $event) {
            // action is 'allow' or 'deny'
            var nsSelector = '.' + namespace,
                enabledMark = action === 'allow' ? '.fi-check' : '.fi-x',
                disabledMark = action === 'allow' ? '.fi-x' : '.fi-check';
            $($event.target).addClass('selected');
            $scope.policyGenerator.find(nsSelector).find(enabledMark).addClass('selected');
            $scope.policyGenerator.find(nsSelector).find(disabledMark).removeClass('selected');
        };
    })
;

