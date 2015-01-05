/**
 * @fileOverview Jasmine Unittest for Roles JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("RolesPage", function() {

    beforeEach(angular.mock.module('RolesPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('RolesCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/roles/roles.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of roleName is empty", function() {
            expect(scope.roleName).toEqual('');
        });

        it("Initial value of roleViewUrl is empty", function() {
            expect(scope.roleViewUrl).toEqual('');
        });
    });

    describe("Function revealModal() Test", function() {

        it("Should set roleName when revealModal() is called", function() {
            scope.revealModal('a', {role_name: "role"});
            expect(scope.roleName).toEqual('role');
        });
    });
});
