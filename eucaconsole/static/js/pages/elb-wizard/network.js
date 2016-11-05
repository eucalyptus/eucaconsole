angular.module('ELBWizard')
.controller('NetworkController', ['$scope', function ($scope) {
    var vm = this;

    vm.vpcNetwork = '';
    vm.securityGroups = [];
    vm.vpcNetworkChoices = [{id:'vpc-123456', label:'vpc-123456'}];
    vm.securityGroupChoices = [{id:'default', label:'default'}];

    // Set initial VPC network choice
    if (vm.vpcNetworkChoices.length) {
        vm.vpcNetwork = vm.vpcNetworkChoices[0];
    }

    // Set initial security groups choice to 'default' group
    if (vm.securityGroupChoices.length) {
        vm.securityGroups = vm.securityGroupChoices.filter(function (sgroup) {
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
