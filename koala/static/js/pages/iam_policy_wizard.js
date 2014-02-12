/**
 * @fileOverview IAM Policy Wizard JS
 * @requires AngularJS
 *
 */

angular.module('IAMPolicyWizard', [])
    .controller('IAMPolicyWizardCtrl', function ($scope, $http) {
        $scope.wizardForm = $('#iam-policy-form');
        $scope.policyJsonEndpoint = '';
        $scope.initController = function (policyJsonEndpoint) {
            $scope.policyJsonEndpoint = policyJsonEndpoint;
        };
        $scope.visitStep = function(step, $event) {
            $event.preventDefault();
            $('#tabStep' + step).click();
        };
        $scope.selectPolicy = function(policyType) {
            var jsonUrl = $scope.policyJsonEndpoint + "?type=" + policyType;
            $http.get(jsonUrl).success(function(oData) {
                var results = oData ? oData['policy'] : '';
                if (results) {
                    $scope.policyText = JSON.stringify(results);
                }
            });
            $('#tabStep3').click();
        };
    })
;

