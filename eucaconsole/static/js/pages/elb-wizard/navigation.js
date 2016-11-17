angular.module('ELBWizard')
.directive('wizardNav', function () {
    return {
        restrict: 'E',
        scope: {
            cloudType: '@',
            vpcEnabled: '@',
            steps: '@'
        },
        templateUrl: '/_template/elbs/wizard/navigation',
        controller: ['$scope', '$location', 'ELBWizardService', function ($scope, $location, ELBWizardService) {
            var navigation = ELBWizardService.validSteps($scope.steps);

            this.validSteps = function () {
                return navigation.steps;
            };

            this.visit = function (step) {
                if(step.complete) {
                    return step.href;
                }
                return '';
            };

            this.status = function (step) {
                var path = $location.path();
                return {
                    active: (path == step.href),
                    disabled: (path != step.href) && !step.complete,
                    complete: step.complete
                };
            };
        }],
        controllerAs: 'nav'
    };
});
