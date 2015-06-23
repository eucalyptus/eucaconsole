/**
 * @fileOverview Elastic Load Balander Security Policy Editor JS
 * @requires AngularJS
 *
 */
angular.module('ELBSecurityPolicyEditor', [])
    .controller('ELBSecurityPolicyEditorCtrl', function ($scope, $timeout) {
        $scope.policyRadioButton = 'existing';
        $scope.initSecurityPolicyEditor = function () {
            $scope.initChosenSelectors();
            $scope.setWatchers();
        };
        $scope.initChosenSelectors = function () {
            $('#ssl_protocols').chosen({width: '100%'});
        };
        $scope.setWatchers = function () {
            $scope.$watch('policyRadioButton', function (newVal) {
                if (newVal === 'new') {
                    $timeout(function() {
                        $scope.initChosenSelectors();
                    }, 100);
                }
            });
        };
    })
;
