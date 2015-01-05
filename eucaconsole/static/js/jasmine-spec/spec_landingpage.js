/**
 * @fileOverview Jasmine Unittest for Landing Page JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("LandingPage", function() {

    beforeEach(angular.mock.module('LandingPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('ItemsCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/instances/instances.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of itemsLoading is true", function() {
            expect(scope.itemsLoading).toBeTruthy();
        });

        it("Initial value of sortBy is empty", function() {
            expect(scope.sortBy).toEqual('');
        });

        it("Initial value of landingPageView is tableview", function() {
            expect(scope.landingPageView).toEqual('tableview');
        });

        it("Initial value of limitCount is 100", function() {
            expect(scope.limitCount).toEqual(100);
        });

        it("Initial value of transitionalRefresh is true", function() {
            expect(scope.transitionalRefresh).toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should set pageResource when initController() is called", function() {
            scope.initController('instances', '[]', 'a');
            expect(scope.pageResource).toEqual('instances');
        });

        it("Should call storeAWSRegion() when initController() is called", function() {
            spyOn(scope, 'storeAWSRegion');
            scope.initController('instances', '[]', 'a');
            expect(scope.storeAWSRegion).toHaveBeenCalled();
        });
    });
});
