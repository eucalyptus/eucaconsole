angular.module('ELBWizard')
.controller('NetworkController', ['$scope', 'ELBWizardService', function ($scope, ELBWizardService) {
    var vm = this;

    vm.vpcNetwork = '';
    vm.securityGroups = [];
    vm.vpcNetworkChoices = ELBWizardService.values.vpcNetworkChoices;
    vm.vpcSecurityGroupChoices = ELBWizardService.values.vpcSecurityGroupChoices;

    // Set initial VPC network choice
    if (vm.vpcNetworkChoices.length) {
        vm.vpcNetwork = vm.vpcNetworkChoices[0];
    }

    // Set initial security groups choice to 'default' group
    if (vm.vpcSecurityGroupChoices.length) {
        vm.securityGroups = vm.vpcSecurityGroupChoices.filter(function (sgroup) {
            return sgroup.id === 'default';
        });
    }

    vm.submit = function () {
        if (vm.networkForm.$invalid) {
            return;
        }

        ELBWizardService.next({});
    };
}]);
