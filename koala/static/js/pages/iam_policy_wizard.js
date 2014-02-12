/**
 * @fileOverview IAM Policy Wizard JS
 * @requires AngularJS
 *
 */

angular.module('IAMPolicyWizard', [])
    .controller('IAMPolicyWizardCtrl', function ($scope) {
        $scope.wizardForm = $('#iam-policy-form');
        $scope.visitStep = function(step, $event) {
            $event.preventDefault();
            $('#tabStep' + step).click();
        };
        $scope.selectPolicy = function(policyType) {
            // TODO: pull in appropriate policy here
            $('#tabStep3').click();
        };
    })
;

