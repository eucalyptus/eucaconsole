angular.module('ELBSecurityPolicyEditorModule', ['ModalModule'])
.directive('securityPolicyEditor', function () {
    return {
        restrict: 'E',
        scope: {
            policy: '=ngModel'
        },
        templateUrl: '/_template/elbs/listener-editor/security-policy',
        controller: ['$scope', 'ModalService', function ($scope, ModalService) {
            var vm = this;
            vm.policyRadioButton = 'existing';
            vm.handleUsePolicy = function ($event) {
                $event.preventDefault();
                if ($scope.securityPolicyForm.$invalid) {
                    return false;
                }
            };
            vm.isShowing = function() {
                return ModalService.isOpen('securityPolicyEditor');
            };
        }],
        controllerAs: 'policyCtrl'
    };
});
