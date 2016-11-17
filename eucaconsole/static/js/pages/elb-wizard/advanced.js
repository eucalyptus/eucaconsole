angular.module('ELBWizard')
.controller('AdvancedController', ['$scope', '$routeParams', 'ELBWizardService', 'ELBService', function ($scope, $routeParams, ELBWizardService, ELBService) {
    this.values = ELBWizardService.values;
    this.createELB = function($event) {
        $event.preventDefault();
        ELBService.createELB($('#csrf_token').val(), this.values).then(
            function success() {
                console.log('created ELB!');
            },
            function failure() {
                console.log('did not ELB!');
            }
        );
    };
}]);

