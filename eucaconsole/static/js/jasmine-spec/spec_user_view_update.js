/**
 * @fileOverview Jasmine Unittest for IAM UserView Update JS 
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
        ctrl = $controller('UserUpdateCtrl', {
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

        it("Initial value of isUserInfoNotChanged is true", function() {
            expect(scope.isUserInfoNotChanged).toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should call setWatch() when initController() is called", function() {
            spyOn(scope, 'setWatch');
            scope.initController();
            expect(scope.setWatch).toHaveBeenCalled();
        });
    });
});
