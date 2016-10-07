angular.module('ELBSecurityPolicyEditorModule', ['ModalModule'])
.directive('securityPolicyEditor', function () {
    return {
        restrict: 'E',
        templateUrl: '/_template/elbs/listener-editor/security-policy',
        controller: ['$scope', function ($scope) {
        }]
    };
});
