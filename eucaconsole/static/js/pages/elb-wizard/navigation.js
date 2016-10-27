angular.module('ELBWizard')
.directive('wizardNav', function () {
    var steps = [
        {
            label: 'General',
            href: '/elbs/wizard/',
            vpcOnly: false,
            complete: false
        },
        {
            label: 'Network',
            href: '/elbs/wizard/network',
            vpcOnly: true,
            complete: false
        },
        {
            label: 'Instances',
            href: '/elbs/wizard/instances',
            vpcOnly: false,
            complete: false
        },
        {
            label: 'Health Check & Advanced',
            href: '/elbs/wizard/advanced',
            vpcOnly: false,
            complete: false
        }
    ];

    return {
        restrict: 'E',
        scope: {
            cloudType: '@cloudType',
            vpcEnabled: '@vpcEnabled'
        },
        templateUrl: '/_template/elbs/wizard/navigation',
        controller: ['$scope', '$location', 'ELBWizardService', function ($scope, $location, ELBWizardService) {
            this.steps = steps;

            this.validSteps = function () {
                return this.steps.filter(function (current) {
                    if($scope.cloudType === 'aws' || $scope.vpcEnabled) {
                        return true;
                    } else {
                        return !current.vpcOnly;
                    }
                });
            };

            this.status = function (step) {
                var path = $location.path();
                return {
                    active: (path == step.href),
                    complete: step.complete
                };
            };
        }],
        controllerAs: 'nav'
    };
});
