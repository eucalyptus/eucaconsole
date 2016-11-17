angular.module('ELBWizard')
.controller('GeneralController', ['$scope', '$route', '$routeParams', 
        '$location', 'ModalService', 'ELBWizardService', 'certificates', 'policies',
    function ($scope, $route, $routeParams, $location, ModalService, ELBWizardService, certificates, policies) {
        this.stepData = {
            certsAvailable: certificates,
            polices: policies
        };
        ELBWizardService.certsAvailable = certificates;
        ELBWizardService.policies = policies;

        this.values = ELBWizardService.values;

        this.submit = function () {
            if($scope.generalForm.$invalid) {
                return;
            }

            ELBWizardService.next({});
        };

        $scope.$on('$destroy', function () {
            ModalService.unregisterModals('securityPolicyEditor', 'certificateEditor');
        });
    }]);
