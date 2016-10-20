/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Jasmine Unittest for Tag Editor JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("Reporting", function() {

    beforeEach(angular.mock.module('ReportingPage'));

    var $rootScope, $location, $compile;
    beforeEach(angular.mock.inject(function(_$location_, _$rootScope_, _$compile_) {
        $rootScope = _$rootScope_;
        $location = _$location_;
        $compile = _$compile_;
    }));

    var controller;
    beforeEach(function() {
        var element = $compile(
            '<dl navigation="" reporting-configured="true"><dd></dd><dd></dd></dl>'
        )($rootScope);
        $rootScope.$digest();

        $location.path('/reporting/dashboard');
        $rootScope.$apply();

        controller = element.controller('navigation');
    });

    describe("initial tab test", function() {
        it("should set preferences path", function() {
            expect($location.path() == '/reporting/preferences').toBe(false);
            controller.setInitialTab('false');
            expect($location.path() == '/reporting/preferences').toBe(true);
        });
    });

    describe("active tab test", function() {
        it("should set active tab state", function() {
            expect(controller.isTabActive('/dashboard') == 'active').toBe(true);
            expect(controller.isTabActive('/reports') == 'active').toBe(false);
            expect(controller.isTabActive('/preferences') == 'active').toBe(false);
            $location.path('/reporting/reports');
            expect(controller.isTabActive('/dashboard') == 'active').toBe(false);
            expect(controller.isTabActive('/reports') == 'active').toBe(true);
            expect(controller.isTabActive('/preferences') == 'active').toBe(false);
            $location.path('/reporting/preferences');
            expect(controller.isTabActive('/dashboard') == 'active').toBe(false);
            expect(controller.isTabActive('/reports') == 'active').toBe(false);
            expect(controller.isTabActive('/preferences') == 'active').toBe(true);
            $location.path('/reporting/blah');
            expect(controller.isTabActive('/dashboard') == 'active').toBe(true);
            expect(controller.isTabActive('/reports') == 'active').toBe(false);
            expect(controller.isTabActive('/preferences') == 'active').toBe(false);
        });
    });
});
