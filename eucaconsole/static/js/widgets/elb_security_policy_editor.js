/**
 * @fileOverview Elastic Load Balander Security Policy Editor JS
 * @requires AngularJS
 *
 */
angular.module('ELBSecurityPolicyEditor', ['EucaConsoleUtils'])
    .controller('ELBSecurityPolicyEditorCtrl', function ($scope, $rootScope) {
        $scope.policyRadioButton = 'existing';
        $scope.policyModal = $('#elb-security-policy-modal');
        $scope.sslProtocols = [];
        $scope.sslCiphers = [];
        $scope.sslServerOrderPref = false;
        $scope.predefinedPolicy = '';
        $scope.initSecurityPolicyEditor = function (latestPredefinedPolicy) {
            $scope.setInitialValues(latestPredefinedPolicy);
            $scope.initChosenSelectors();
        };
        $scope.setInitialValues = function (latestPredefinedPolicy) {
            $scope.predefinedPolicy = latestPredefinedPolicy;
            $scope.sslProtocols = $scope.policyModal.find('#ssl_protocols').val();
        };
        $scope.initChosenSelectors = function () {
            $('#ssl_protocols').chosen({width: '100%'});
            $('#ssl_ciphers').chosen({width: '100%', search_contains: true});
        };
        $scope.setSecurityPolicy = function () {
            // TODO: Perform validation checks
            var elbForm = $('#elb-form'),
                selectedPolicyName,
                customPolicyPlaceholder = 'ELB-CustomSecurityPolicy',
                serverOrderPrefInput = elbForm.find('#ssl_server_order_pref_hidden_input'),
                sslUsingCustomPolicy = elbForm.find('#ssl_using_custom_policy');
            elbForm.find('#security_policy_updated').prop('checked', true);
            elbForm.find('#ssl_protocols_hidden_input').val(JSON.stringify($scope.sslProtocols));
            elbForm.find('#ssl_ciphers_hidden_input').val(JSON.stringify($scope.sslCiphers));
            elbForm.find('#predefined_policy_hidden_input').val($scope.predefinedPolicy);
            serverOrderPrefInput.prop('checked', $scope.sslServerOrderPref);
            sslUsingCustomPolicy.prop('checked', $scope.policyRadioButton === 'new');
            selectedPolicyName = $scope.policyRadioButton === 'existing'? $scope.predefinedPolicy: customPolicyPlaceholder;
            $rootScope.$broadcast('elb:securityPolicySelected', selectedPolicyName);
            $scope.policyModal.foundation('reveal', 'close');
        };
    })
;
