/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
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
        $scope.policyModal.on('opened.fndtn.reveal', function () {
            // TODO: Find a better workaround here
            // Although this isn't ideal, we're re-jiggering the field values when the ELB security policy
            //   modal is subsequently opened in the Create ELB wizard to display the selected policy settings
            if ($scope.policyRadioButton === 'existing') {  // Predefined security policy
                $scope.policyModal.find('#policy-type-predefined').prop('checked', true);
                if ($scope.predefinedPolicy) {
                    $scope.policyModal.find('#predefined_policy').val($scope.predefinedPolicy);
                }
            } else {  // Custom security policy
                $scope.policyModal.find('#policy-type-new').prop('checked', true);
                $scope.policyModal.find('#ssl_protocols').val($scope.sslProtocols).trigger('chosen:updated');
                $scope.policyModal.find('#ssl_ciphers').val($scope.sslCiphers).trigger('chosen:updated');
                $scope.policyModal.find('#server_order_preference').prop('checked', $scope.sslServerOrderPref);
            }
        });
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
