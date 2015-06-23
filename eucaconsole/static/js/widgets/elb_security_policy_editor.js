/**
 * @fileOverview Elastic Load Balander Security Policy Editor JS
 * @requires AngularJS
 *
 */
angular.module('ELBSecurityPolicyEditor', [])
    .controller('ELBSecurityPolicyEditorCtrl', function ($scope) {
        $scope.policyRadioButton = 'existing';
        $scope.initSecurityPolicyEditor = function () {
            $scope.initChosenSelectors();
        };
        $scope.initChosenSelectors = function () {
            $('#ssl_protocols').chosen({width: '100%'});
            $('#ssl_ciphers').chosen({width: '100%', search_contains: true});
        };
    })
;
