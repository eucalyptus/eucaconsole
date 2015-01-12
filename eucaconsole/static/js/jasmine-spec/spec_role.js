/**
 * @fileOverview Jasmine Unittest for IAM Role JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("RolePage", function() {

    beforeEach(angular.mock.module('RolePage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('RolePageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/roles/role_view.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of trustPolicy is empty", function() {
            expect(scope.trustPolicy).toEqual('');
        });

        it("Initial value of trustedEntity is empty", function() {
            expect(scope.trustedEntity).toEqual('');
        });

        it("Initial value of codeEditor is null", function() {
            expect(scope.codeEditor).toEqual(null);
        });
    });

    describe("Function initController() Test", function() {

        it("Should set allUsers when initController() is called", function() {
            scope.initController('a', 'b', 'c');
            expect(scope.allUsers).toEqual('a');
        });

        it("Should set trustPolicy when initController() is called", function() {
            scope.initController('a', 'b', 'c');
            expect(scope.trustPolicy).toEqual('b');
        });

        it("Should set trustedEntity when initController() is called", function() {
            scope.initController('a', 'b', 'c');
            expect(scope.trustedEntity).toEqual('c');
        });

        it("Should call initCodeMirror() when initController() is called", function() {
            spyOn(scope, 'initCodeMirror');
            scope.initController('a', 'b', 'c');
            expect(scope.initCodeMirror).toHaveBeenCalled();
        });
    });
});
