/**
 * @fileOverview Jasmine Unittest for Scalinggroup Policy JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("ScalingGroupPolicy", function() {

    beforeEach(angular.mock.module('ScalingGroupPolicy'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('ScalingGroupPolicyCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/scalinggroups/scalinggroup_policy.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of policyName is empty", function() {
            expect(scope.policyName).toEqual('');
        });

        it("Initial value of adjustmentAmount is 1", function() {
            expect(scope.adjustmentAmount).toEqual(1);
        });

        it("Initial value of coolDown is 300", function() {
            expect(scope.coolDown).toEqual(300);
        });

        it("Initial value of isNotValid is true", function() {
            expect(scope.isNotValid).toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should call setWatch() when initController() is called", function() {
            spyOn(scope, 'setWatch');
            scope.initController('[]');
            expect(scope.setWatch).toHaveBeenCalled();
        });
    });
});
