/**
 * @fileOverview Jasmine Unittest for Policy List JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("PolicyList", function() {

    beforeEach(angular.mock.module('PolicyList'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('PolicyListCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/panels/policy_list.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of policyIndex is -1", function() {
            expect(scope.policyIndex).toEqual(-1);
        });

        it("Initial value of policyName is empty", function() {
            expect(scope.policyName).toEqual('');
        });
    });

    describe("Function initPolicies() Test", function() {

        it("Should call getPolicies() when initPolicies() is called", function() {
            spyOn(scope, 'getPolicies');
            scope.initPolicies('a', 'b', 'c', 'd');
            expect(scope.getPolicies).toHaveBeenCalled();
        });
    });
});
