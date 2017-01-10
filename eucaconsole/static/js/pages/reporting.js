/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview ElasticIP Detail Page JS
 * @requires AngularJS
 *
 */

angular.module('ReportingPage', ['ngRoute', 'localytics.directives', 'EucaConsoleUtils', 'ModalModule', 'BucketServiceModule', 'CreateBucketModule', 'ReportingServiceModule'])
.directive('navigation', function () {
    return {
        restrict: 'A',
        link: function (scope, element, attrs, ctrl) {
             ctrl.setInitialTab(attrs.reportingConfigured);
        },
        controller: ['$scope', '$location', function ($scope, $location) {
            this.isTabActive = function(name) {
                var path = $location.path();
                if (path.indexOf(name) > -1)
                    return 'active';
                // this handles case where url path contains something other than reports or prefs, but
                // falls back to dashboard tab due to router .otherwise clause
                if (name === '/dashboard' &&
                    ['/reports', '/preferences'].every(function(val) { return path.indexOf(val) === -1; }) )
                    return 'active';
                return '';
            };
            this.setInitialTab = function(reportingConfigured) {
                if (reportingConfigured !== 'true') {
                    $location.path('/reporting/preferences');
                }
            };
        }],
        controllerAs: 'nav'
    };
})
.controller('DashboardController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    console.log('dashboard');
    // would be nice to keep this controller function in a separate file to avoid this getting bloated
}])
.controller('ReportsController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    console.log('reports');
    // would be nice to keep this controller function in a separate file to avoid this getting bloated
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

