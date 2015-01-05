/**
 * @fileOverview Jasmine Unittest for IAM UserView Password JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("UserView", function() {

    beforeEach(angular.mock.module('UserView'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('UserPasswordCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/users/user_view.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of jsonRandomEndpoint is empty", function() {
            expect(scope.jsonRandomEndpoint).toEqual('');
        });

        it("Initial value of jsonDeleteEndpoint is empty", function() {
            expect(scope.jsonDeleteEndpoint).toEqual('');
        });

        it("Initial value of jsonChangeEndpoint is empty", function() {
            expect(scope.jsonChangeEndpoint).toEqual('');
        });

        it("Initial value of getFileEndpoint is empty", function() {
            expect(scope.getFileEndpoint).toEqual('');
        });

        it("Initial value of data is empty", function() {
            expect(scope.data).toEqual('');
        });

        it("Initial value of has_password is false", function() {
            expect(scope.has_password).not.toBeTruthy();
        });

        it("Initial value of isPasswordNotChanged is true", function() {
            expect(scope.isPasswordNotChanged).toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should set has_password when initController() is called", function() {
            scope.initController('a', 'b', 'c', 'd', 'e');
            expect(scope.has_password).toEqual('e');
        });

        it("Should call setWatch() when initController() is called", function() {
            spyOn(scope, 'setWatch');
            scope.initController('a', 'b', 'c', 'd', 'e');
            expect(scope.setWatch).toHaveBeenCalled();
        });
    });
});
