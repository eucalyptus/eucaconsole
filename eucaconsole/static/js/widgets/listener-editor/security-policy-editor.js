angular.module('ELBSecurityPolicyEditorModule', ['ModalModule', 'EucaConsoleUtils'])
.directive('securityPolicyEditor', function () {
    return {
        restrict: 'E',
        scope: {
            policy: '=ngModel'
        },
        // values the policy needs
        // values.policy.securityPolicyUpdated,
        // values.policy.sslUsingCustomPolicy,
        // values.policy.predefiedPolicy,
        // values.policy.sslProtocols,
        // values.policy.sslCiphers,
        // values.policy.sslServerOrderPref,
        templateUrl: '/_template/elbs/listener-editor/security-policy',
        controller: ['$scope', '$timeout', 'ModalService', 'ELBWizardService', 'eucaHandleError', function ($scope, $timeout, ModalService, ELBWizardService, eucaHandleError) {
            var vm = this;
            vm.policyRadioButton = 'existing';
            vm.predefinedPolicyChoices = ELBWizardService.values.policy.predefinedPolicyChoices;
            vm.protocolChoices = [
                {id:'Protocol-TLSv1.2', label:'TLSv1.2'},
                {id:'Protocol-TLSv1.1', label:'TLSv1.1'},
                {id:'Protocol-TLSv1', label:'TLSv1'},
            ];
            vm.cipherChoices = [
                'ECDHE-ECDSA-AES128-GCM-SHA256',
                'ECDHE-RSA-AES128-GCM-SHA256',
                'ECDHE-ECDSA-AES128-SHA256',
                'ECDHE-RSA-AES128-SHA256',
                'ECDHE-ECDSA-AES128-SHA',
                'ECDHE-RSA-AES128-SHA',
                'DHE-RSA-AES128-SHA',
                'ECDHE-ECDSA-AES256-GCM-SHA384',
                'ECDHE-RSA-AES256-GCM-SHA384',
                'ECDHE-ECDSA-AES256-SHA384',
                'ECDHE-RSA-AES256-SHA384',
                'ECDHE-RSA-AES256-SHA',
                'ECDHE-ECDSA-AES256-SHA',
                'AES128-GCM-SHA256',
                'AES128-SHA256',
                'AES128-SHA',
                'AES256-GCM-SHA384',
                'AES256-SHA256',
                'AES256-SHA',
                'DHE-DSS-AES128-SHA',
                'CAMELLIA128-SHA',
                'EDH-RSA-DES-CBC3-SHA',
                'DES-CBC3-SHA',
                'DHE-DSS-AES256-GCM-SHA384',
                'DHE-RSA-AES256-GCM-SHA384',
                'DHE-RSA-AES256-SHA256',
                'DHE-DSS-AES256-SHA256',
                'DHE-RSA-AES256-SHA',
                'DHE-DSS-AES256-SHA',
                'DHE-RSA-CAMELLIA256-SHA',
                'DHE-DSS-CAMELLIA256-SHA',
                'CAMELLIA256-SHA',
                'EDH-DSS-DES-CBC3-SHA',
                'DHE-DSS-AES128-GCM-SHA256',
                'DHE-RSA-AES128-GCM-SHA256',
                'DHE-RSA-AES128-SHA256',
                'DHE-DSS-AES128-SHA256',
                'DHE-RSA-CAMELLIA128-SHA',
                'DHE-DSS-CAMELLIA128-SHA',
                'ADH-AES128-GCM-SHA256',
                'ADH-AES128-SHA',
                'ADH-AES128-SHA256',
                'ADH-AES256-GCM-SHA384',
                'ADH-AES256-SHA',
                'ADH-AES256-SHA256',
                'ADH-CAMELLIA128-SHA',
                'ADH-CAMELLIA256-SHA',
                'ADH-DES-CBC3-SHA',
                'ADH-DES-CBC-SHA',
                'ADH-SEED-SHA',
                'DES-CBC-SHA',
                'DHE-DSS-SEED-SHA',
                'DHE-RSA-SEED-SHA',
                'EDH-DSS-DES-CBC-SHA',
                'EDH-RSA-DES-CBC-SHA',
                'IDEA-CBC-SHA',
                'SEED-SHA',
                'DES-CBC3-MD5',
                'DES-CBC-MD5',
            ];
            vm.handleUsePolicy = function ($event) {
                $event.preventDefault();
                if ($scope.securityPolicyForm.$invalid) {
                    return false;
                }
                if (vm.policyRadioButton === 'new') {
                    $scope.policy.sslUsingCustomPolicy = 'on';
                }
                else {
                    $scope.policy.sslUsingCustomPolicy = undefined;
                }
                ModalService.closeModal('securityPolicyEditor');
            };
        }],
        controllerAs: 'policyCtrl'
    };
});
