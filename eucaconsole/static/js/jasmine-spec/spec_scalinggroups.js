/**
 * @fileOverview Jasmine Unittest for Scaling Groups JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("ScalingGroupsPage", function() {

    beforeEach(angular.mock.module('ScalingGroupsPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('ScalingGroupsCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/scalinggroups/scalinggroups.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of scalinggroupID is empty", function() {
            expect(scope.scalinggroupID).toEqual('');
        });

        it("Initial value of scalinggroupName is empty", function() {
            expect(scope.scalinggroupName).toEqual('');
        });

        it("Initial value of scalinggroupInstances is empty", function() {
            expect(scope.scalinggroupInstances).toEqual('');
        });
    });

    describe("Function revealModal() Test", function() {

        it("Should set scalinggroupID when revealModal() is called", function() {
            scope.revealModal('a', {id: "sg-12345678"});
            expect(scope.scalinggroupID).toEqual('sg-12345678');
        });

        it("Should set scalinggroupName when revealModal() is called", function() {
            scope.revealModal('a', {name: "sgname"});
            expect(scope.scalinggroupName).toEqual('sgname');
        });

        it("Should set scalinggroupInstances when revealModal() is called", function() {
            scope.revealModal('a', {current_instances_count: 3});
            expect(scope.scalinggroupInstances).toEqual(3);
        });
    });
});
