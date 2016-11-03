angular.module('ELBWizard', [
    'ngRoute', 'TagEditorModule', 'ELBListenerEditorModule', 'localytics.directives',
    'ELBSecurityPolicyEditorModule', 'ELBCertificateEditorModule', 'ModalModule'
])
.factory('ELBWizardService', ['$location', function ($location) {
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

    function Navigation (steps) {
        steps = steps || [];
        this.steps = steps.map(function (current, index, ary) {
            current._next = ary[index + 1];
            return current;
        });
        this.current = this.steps[0];
    }

    Navigation.prototype.next = function () {
        this.current = this.current._next;
        return this.current;
    };

    var svc = {
        certsAvailable: [],
        policies: [],
        values: {},

        validSteps: function (cloudType, vpcEnabled) {
            var validSteps = steps.filter(function (current) {
                if(cloudType === 'aws' || vpcEnabled) {
                    return true;
                } else {
                    return !current.vpcOnly;
                }
            });
            this.nav = new Navigation(validSteps);
            return this.nav;
        },

        next: function (params) {
            angular.merge(this.values, params);

            this.nav.current.complete = true;
            var next = this.nav.next();
            $location.path(next.href);
        },

        submit: function () {
        }
    };
    return svc;
}])
.directive('stepData', function () {
    return {
        restrict: 'A',
        scope: {
            stepData: '='
        },
        controller: ['$scope', function ($scope) {
            angular.merge(this, $scope.stepData);
        }]
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
.config(function ($routeProvider, $locationProvider) {
    var certificatePromise;

    $routeProvider
        .when('/elbs/wizard/', {
            templateUrl: '/_template/elbs/wizard/general',
            controller: 'GeneralController',
            controllerAs: 'general',
            resolve: {
                policies: function ($q) {
                    return $q.when('foo');
                },
                certificates: ['CertificateService', function (CertificateService) {
                    if(!certificatePromise) {
                        certificatePromise = CertificateService.getCertificates();
                    }
                    return certificatePromise;
                }]
            }
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
