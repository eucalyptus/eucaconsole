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
        this.listeners = [{
            'fromPort': 80,
            'toPort': 80,
            'fromProtocol': 'HTTP',
            'toProtocol': 'HTTP'
        }];

        this.submit = function () {
            if($scope.generalForm.$invalid) {
                return;
            }

            ELBWizardService.next({
                name: this.elbName,
                listeners: this.listeners,
                tags: this.tags
            });
        };

        $scope.$on('$destroy', function () {
            ModalService.unregisterModals('securityPolicyEditor', 'certificateEditor');
        });
    }]);
