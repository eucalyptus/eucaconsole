/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview ElasticIP Detail Page JS
 * @requires AngularJS
 *
 */

angular.module('ReportingPage', ['ngRoute'])
.directive('navigation', function ($location) {
    return {
        restrict: 'A',
        scope: {
            reportingConfigured: '@reportingConfigured'
        },
        link: function (scope, elems, attrs) {
            scope.tabs = {'dashboard': false, 'reports': false, 'preferences': true};
            scope.isTabActive = function(name) {
                return (name.indexOf($location.path()) > -1)?'active':'';
            };
            if (scope.reportingConfigured !== 'true') {
                $location.path('/reporting/preferences');
            }
        }
    };
})
.controller('DashboardController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    console.log('dashboard');
}])
.controller('ReportsController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    console.log('reports');
}])
.controller('PreferencesController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    console.log('preferences');
}])
.config(function ($routeProvider, $locationProvider) {
    $routeProvider
        .when('/reporting/reports', {
            templateUrl: '/_template/reporting/reporting_reports',
            controller: 'ReportsController',
            controllerAs: 'reports'
        })
        .when('/reporting/preferences', {
            templateUrl: '/_template/reporting/reporting_preferences',
            controller: 'PreferencesController',
            controllerAs: 'preferences'
        })
        .otherwise({
            templateUrl: '/_template/reporting/reporting_dashboard',
            controller: 'DashboardController',
            controllerAs: 'dashboard',
        });

    $locationProvider.html5Mode(true);
});

