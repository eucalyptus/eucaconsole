/**
 * @fileOverview Jasmine Unittest for Security groups JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("SecurityGroupsPage", function() {

    beforeEach(angular.mock.module('SecurityGroupsPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('SecurityGroupsCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/securitygroups/securitygroups.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of securitygroupID is empty", function() {
            expect(scope.securitygroupID).toEqual('');
        });

        it("Initial value of securitygroupName is undefined", function() {
            expect(scope.securitygroupName).toEqual(undefined);
        });
    });

    describe("Function revealModal() Test", function() {

        it("Should set securitygroupID when revealModal() is called", function() {
            scope.revealModal('a', {id: "sg-12345678"});
            expect(scope.securitygroupID).toEqual('sg-12345678');
        });

        it("Should set securitygroupName when revealModal() is called", function() {
            scope.revealModal('a', {name: "sg"});
            expect(scope.securitygroupName).toEqual('sg');
        });
    });
});
