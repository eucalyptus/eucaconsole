angular.module('ELBSecurityPolicyEditorModule', ['ModalModule'])
.directive('securityPolicyEditor', function () {
    return {
        restrict: 'E',
        scope: {
            policy: '=ngModel'
        },
        templateUrl: '/_template/elbs/listener-editor/security-policy',
        controller: ['$scope', function ($scope) {
        }]
    };
});
