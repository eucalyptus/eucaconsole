/**
 * @fileOverview Jasmine Unittest for IAM UserNew JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("UserNew", function() {

    beforeEach(angular.mock.module('UserNew'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('UserNewCtrl', {
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

        it("Initial value of submitEndpoint is empty", function() {
            expect(scope.submitEndpoint).toEqual('');
        });

        it("Initial value of allUsersRedirect is empty", function() {
            expect(scope.allUsersRedirect).toEqual('');
        });

        it("Initial value of quotas_expanded is false", function() {
            expect(scope.quotas_expanded).not.toBeTruthy();
        });

        it("Initial value of isNotValid is true", function() {
            expect(scope.isNotValid).toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should set submitEndpoint when initController() is called", function() {
            scope.initController('a', 'b', 'c', 'd', 'e');
            expect(scope.submitEndpoint).toEqual('a');
        });

        it("Should call setWatch() when initController() is called", function() {
            spyOn(scope, 'setWatch');
            scope.initController('a', 'b', 'c', 'd', 'e');
            expect(scope.setWatch).toHaveBeenCalled();
        });
    });
});
