angular.module('ELBWizard', [
    'ngRoute', 'TagEditorModule', 'ELBListenerEditorModule', 'localytics.directives',
    'ELBSecurityPolicyEditorModule', 'ELBCertificateEditorModule', 'ModalModule'
])
.factory('ELBWizardService', function () {
    var svc = {};
    return svc;
})
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
