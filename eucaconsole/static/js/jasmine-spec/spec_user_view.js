/**
 * @fileOverview Jasmine Unittest for IAM UserView JS 
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
        ctrl = $controller('UserViewCtrl', {
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

        it("Initial value of disable_url is empty", function() {
            expect(scope.disable_url).toEqual('');
        });

        it("Initial value of allUsersRedirect is empty", function() {
            expect(scope.allUsersRedirect).toEqual('');
        });

        it("Initial value of ec2_expanded is false", function() {
            expect(scope.ec2_expanded).not.toBeTruthy();
        });

        it("Initial value of s3_expanded is false", function() {
            expect(scope.s3_expanded).not.toBeTruthy();
        });

        it("Initial value of currentTab is general-tab", function() {
            expect(scope.currentTab).toEqual('general-tab');
        });

        it("Initial value of isSubmitted is false", function() {
            expect(scope.isSubmitted).not.toBeTruthy();
        });

        it("Initial value of isNotChanged is true", function() {
            expect(scope.isNotChanged).toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should set userName when initController() is called and user_name JSON is set", function() {
            scope.initController('{"user_name": "username"}');
            expect(scope.userName).toEqual('username');
        });

        it("Should call setWatch() when initController() is called", function() {
            spyOn(scope, 'setWatch');
            scope.initController('{}');
            expect(scope.setWatch).toHaveBeenCalled();
        });
    });
});
