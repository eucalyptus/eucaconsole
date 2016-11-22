angular.module('ELBWizard')
.directive('wizardNav', function () {
    return {
        restrict: 'E',
        require: '?^elbWizard',
        templateUrl: '/_template/elbs/wizard/navigation',
        link: function (scope, element, attributes, ctrl) {
            var steps = ctrl.validSteps();
            scope.setNav(steps);
        },
        controller: ['$scope', '$location', 'ELBWizardService', function ($scope, $location, ELBWizardService) {
            $scope.setNav = function (steps) {
                $scope.navigation = ELBWizardService.initNav(steps);
            };

            this.validSteps = function () {
                return $scope.navigation.steps;
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
