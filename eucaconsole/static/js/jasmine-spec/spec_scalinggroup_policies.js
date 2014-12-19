/**
 * @fileOverview Jasmine Unittest for Scalinggroup Policies JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("ScalingGroupPolicies", function() {

    beforeEach(angular.mock.module('ScalingGroupPolicies'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('ScalingGroupPoliciesCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/scalinggroups/scalinggroup_policies.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of policyName is empty", function() {
            expect(scope.policyName).toEqual('');
        });
    });

    describe("Function initPage() Test", function() {

        it("Should call setFocus() when initPage() is called", function() {
            spyOn(scope, 'setFocus');
            scope.initPage();
            expect(scope.setFocus).toHaveBeenCalled();
        });
    });
});
