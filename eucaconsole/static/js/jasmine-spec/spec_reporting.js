/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Jasmine Unittest for reporting page
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

    describe("#initialTabTest", function() {
        it("should set preferences path", function() {
            expect($location.path() == '/reporting/preferences').toBe(false);
            controller.setInitialTab('false');
            expect($location.path() == '/reporting/preferences').toBe(true);
        });
    });

    describe("#activeTabTest", function() {
        it("should activate default tab", function() {
            expect(controller.isTabActive('/dashboard') == 'active').toBe(true);
            expect(controller.isTabActive('/reports') == 'active').toBe(false);
            expect(controller.isTabActive('/preferences') == 'active').toBe(false);
        });

        it("should activate reports tab", function() {
            $location.path('/reporting/reports');
            expect(controller.isTabActive('/dashboard') == 'active').toBe(false);
            expect(controller.isTabActive('/reports') == 'active').toBe(true);
            expect(controller.isTabActive('/preferences') == 'active').toBe(false);
        });

        it("should activate preferences tab", function() {
            $location.path('/reporting/preferences');
            expect(controller.isTabActive('/dashboard') == 'active').toBe(false);
            expect(controller.isTabActive('/reports') == 'active').toBe(false);
            expect(controller.isTabActive('/preferences') == 'active').toBe(true);
        });

        it("should activate default tab with bad path spec", function() {
            $location.path('/reporting/blah');
            expect(controller.isTabActive('/dashboard') == 'active').toBe(true);
            expect(controller.isTabActive('/reports') == 'active').toBe(false);
            expect(controller.isTabActive('/preferences') == 'active').toBe(false);
        });
    });
});
