/**
 * @fileOverview Jasmine Unittest for Dashboard JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("Dashboard", function() {

    beforeEach(angular.mock.module('Dashboard'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('DashboardCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/dashboard.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of jsonEndpoint is empty", function() {
            expect(scope.jsonEndpoint).toEqual('');
        });

        it("Initial value of statusEndpoint is empty", function() {
            expect(scope.statusEndpoint).toEqual('');
        });

        it("Initial value of selectedZone is empty", function() {
            expect(scope.selectedZone).toEqual('');
        });

        it("Initial value of storedZoneKey is empty", function() {
            expect(scope.storedZoneKey).toEqual('');
        });

        it("Initial value of itemsLoading is true", function() {
            expect(scope.itemsLoading).toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should set jsonEndpoint when initController() is called and json_items_url JSON is set", function() {
            scope.initController('{"json_items_url": "endpoint"}');
            expect(scope.jsonEndpoint).toEqual('endpoint');
        });

        it("Should call setInitialZone() when initController() is called", function() {
            spyOn(scope, 'setInitialZone');
            scope.initController('{}');
            expect(scope.setInitialZone).toHaveBeenCalled();
        });
    });
});
