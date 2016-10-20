/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Jasmine Unittest for Tag Editor JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("Reporting", function() {

    beforeEach(angular.mock.module('Reporting'));

    var $scope, $location;
    beforeEach(angular.mock.inject(function(_$location_, _$rootScaope_) {
        $location = _$location_;
        $scope = _$rootScope_.$new();
    }));

    beforeEach(function() {
        var template = window.__html__['templates/reporting/reporting.pt'];
        setFixtures(template);
    });

    describe("initial tab test", function() {
        it("should set preferences path", function() {
            $location.path('/reporting/dashboard');
            expect(location.path() == '/reporting/preferences').toBe(false);
            scope.setInitialTab('false');
            expect(location.path() == '/reporting/preferences').toBe(true);
        });
    });
});
