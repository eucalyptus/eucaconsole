angular.module('ELBWizard')
.controller('GeneralController', ['$scope', '$route', '$routeParams', 
        '$location', 'ModalService', 'ELBWizardService', 'certificates', 'policies',
    function ($scope, $route, $routeParams, $location, ModalService, ELBWizardService, certificates, policies) {
        var vm = this;

        ELBWizardService.certsAvailable = certificates;
        ELBWizardService.policies = policies;

        this.values = ELBWizardService.values;

        this.submit = function () {
            if($scope.generalForm.$invalid) {
                return;
            }

            ELBWizardService.next({});
        };

        this.isHTTPSListenerDefined = function() {
            return vm.values.listeners.findIndex(function(val) {
                return val.fromProtocol == "HTTPS";
            }) > -1;
        };

        this.openPolicyModal = function () {
            ModalService.openModal('securityPolicyEditor');
        };

        $scope.$on('$destroy', function () {
            ModalService.unregisterModals('securityPolicyEditor', 'certificateEditor');
        });
    }]);
