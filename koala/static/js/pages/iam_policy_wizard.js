/**
 * @fileOverview IAM Policy Wizard JS
 * @requires AngularJS
 *
 */

angular.module('IAMPolicyWizard', [])
    .controller('IAMPolicyWizardCtrl', function ($scope, $http) {
        $scope.wizardForm = $('#iam-policy-form');
        $scope.policyJsonEndpoint = '';
        $scope.policyTextarea = $('#policy');
        $scope.codeEditor = null;
        $scope.initController = function (policyJsonEndpoint) {
            $scope.policyJsonEndpoint = policyJsonEndpoint;
            $scope.initCodeMirror();
        };
        $scope.initCodeMirror = function () {
            $scope.codeEditor = CodeMirror.fromTextArea(document.getElementById('policy'), {
                mode: "javascript",
                lineWrapping: true
            });
        };
        $scope.visitStep = function(step, $event) {
            $event.preventDefault();
            $('#tabStep' + step).click();
        };
        $scope.selectPolicy = function(policyType) {
            var jsonUrl = $scope.policyJsonEndpoint + "?type=" + policyType;
            $http.get(jsonUrl).success(function(oData) {
                var results = oData ? oData['policy'] : '',
                    formattedResults = '';
                if (results) {
                    formattedResults = JSON.stringify(results, null, 2);
                    $scope.codeEditor.setValue(formattedResults);
                }
            });
            $('#tabStep3').click();
        };
    })
;

