angular.module('ELBWizard', ['ngRoute'])
.controller('MainController', function () {
    console.log('main');
})
.controller('GeneralController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    console.log('general');
}])
.controller('NetworkController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    console.log('network');
}])
.config(function ($routeProvider, $locationProvider) {
    $routeProvider
        .when('/elbs/wizard/', {
            template: 'General',
            controller: 'GeneralController',
            controllerAs: 'general'
        })
        .when('/elbs/wizard/network', {
            template: 'Network',
            controller: 'NetworkController',
            controllerAs: 'network'
        })
        .when('/elbs/wizard/instances', {
            template: 'Instances',
            controller: 'InstancesController',
            controllerAs: 'instances'
        })
        .when('/elbs/wizard/advanced', {
            template: 'Advanced',
            controller: 'AdvancedController',
            controllerAs: 'advanced'
        });

    //  Enable HTML5 mode when we've gotten far enough for url rewriting
    $locationProvider.html5Mode(true);
});
