angular.module('ELBWizard')
.controller('NetworkController', ['$scope', 'ELBWizardService', function ($scope, ELBWizardService) {
    var vm = this;

    vm.vpcNetwork = ELBWizardService.values.vpcNetwork;
    vm.vpcNetworkChoices = ELBWizardService.values.vpcNetworkChoices;
    vm.vpcSecurityGroups = ELBWizardService.values.vpcSecurityGroups;
    vm.vpcSecurityGroupChoices = ELBWizardService.values.vpcSecurityGroupChoices;

    vm.submit = function () {
        if (vm.networkForm.$invalid) {
            return;
        }

        ELBWizardService.next({});
    };
}]);
