/**
 * @fileOverview Jasmine Unittest for Scalinggroup Instances JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("ScalingGroupInstances", function() {

    beforeEach(angular.mock.module('ScalingGroupInstances'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('ScalingGroupInstancesCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/scalinggroups/scalinggroup_instances.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of loading is false", function() {
            expect(scope.loading).not.toBeTruthy();
        });

        it("Initial value of instanceID is empty", function() {
            expect(scope.instanceID).toEqual('');
        });

        it("Initial value of jsonEndpoint is empty", function() {
            expect(scope.jsonEndpoint).toEqual('');
        });

        it("Initial value of initialLoading is true", function() {
            expect(scope.initialLoading).toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should set jsonEndpoint when initController() is called", function() {
            scope.initController('url');
            expect(scope.jsonEndpoint).toEqual('url');
        });

        it("Should call getItems() when initController() is called", function() {
            spyOn(scope, 'getItems');
            scope.initController('url');
            expect(scope.getItems).toHaveBeenCalled();
        });
    });
});
