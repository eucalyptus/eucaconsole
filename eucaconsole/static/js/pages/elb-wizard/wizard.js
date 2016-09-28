angular.module('ELBWizard', [
    'ngRoute', 'TagEditorModule', 'ELBListenerEditorModule',
    'ELBSecurityPolicyEditorModule'
])
.factory('ELBWizardService', function () {
    var svc = {};
    return svc;
})
.directive('wizardNav', function () {
    var steps = [
        {
            label: 'General',
            href: '/elbs/wizard/',
            vpcOnly: false,
            complete: false
        },
        {
            label: 'Instances',
            href: '/elbs/wizard/instances',
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
})
.directive('focusOnLoad', function ($timeout) {
    return {
        restrict: 'A',
        link: function (scope, elem) {
            $timeout(function () {
                elem[0].focus();
            });
        }
    };
})
.controller('MainController', function () {
})
.controller('GeneralController', ['$scope', '$route', '$routeParams', '$location', function ($scope, $route, $routeParams, $location) {
    this.listeners = [{
        'fromPort': 80,
        'toPort': 80,
        'fromProtocol': 'HTTP',
        'toProtocol': 'HTTP'
    }];

    this.submit = function () {
        $location.path('/elbs/wizard/instances');
    };
}])
.controller('NetworkController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    console.log('network');
}])
.controller('InstancesController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    console.log('instances');
}])
.controller('AdvancedController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    console.log('advanced');
}])
.config(function ($routeProvider, $locationProvider) {
    $routeProvider
        .when('/elbs/wizard/', {
            templateUrl: '/_template/elbs/wizard/general',
            controller: 'GeneralController',
            controllerAs: 'general',
            resolve: {
                policies: function ($q) {
                    return $q.when('foo');
                },
                certificates: function () {
                    return 'bar';
                }
            },
            resolveAs: 'myfuckingresolve'
        })
        .when('/elbs/wizard/network', {
            templateUrl: '/_template/elbs/wizard/network',
            controller: 'NetworkController',
            controllerAs: 'network'
        })
        .when('/elbs/wizard/instances', {
            templateUrl: '/_template/elbs/wizard/instances',
            controller: 'InstancesController',
            controllerAs: 'instances'
        })
        .when('/elbs/wizard/advanced', {
            templateUrl: '/_template/elbs/wizard/advanced',
            controller: 'AdvancedController',
            controllerAs: 'advanced'
        });

    $locationProvider.html5Mode(true);
});
