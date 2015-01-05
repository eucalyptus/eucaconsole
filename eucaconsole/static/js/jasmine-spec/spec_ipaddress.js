/**
 * @fileOverview Jasmine Unittest for IP Address JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("ElasticIPPage", function() {

    beforeEach(angular.mock.module('ElasticIPPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('ElasticIPPageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/ipaddresses/ipaddress_view.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of publicIP is empty", function() {
            expect(scope.publicIP).toEqual('');
        });

        it("Initial value of allocationID is empty", function() {
            expect(scope.allocationID).toEqual('');
        });
    });

    describe("Function initController() Test", function() {

        it("Should set publicIP when initController() is called", function() {
            scope.initController('10.0.0.0', '12345678');
            expect(scope.publicIP).toEqual('10.0.0.0');
        });

        it("Should allocationID when initController() is called", function() {
            scope.initController('10.0.0.0', '12345678');
            expect(scope.allocationID).toEqual('12345678');
        });

        it("Should call activateWidget() when initController() is called", function() {
            spyOn(scope, 'activateWidget');
            scope.initController('10.0.0.0', '12345678');
            expect(scope.activateWidget).toHaveBeenCalled();
        });
    });
});
