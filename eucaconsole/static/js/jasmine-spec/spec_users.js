/**
 * @fileOverview Jasmine Unittest for IAM Users JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("UsersPage", function() {

    beforeEach(angular.mock.module('UsersPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('UsersCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/users/users.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of userName is empty", function() {
            expect(scope.userName).toEqual('');
        });

        it("Initial value of groupName is empty", function() {
            expect(scope.groupName).toEqual('');
        });
    });

    describe("Function revealDelete() Test", function() {

        it("Should set userName when revealDelete() is called", function() {
            scope.revealDelete({user_name: "username"});
            expect(scope.userName).toEqual('username');
        });
    });

    describe("Function revealModalXHP() Test", function() {

        it("Should set userName when revealModalXHR() is called", function() {
            scope.revealModalXHR('a', {user_name: "username"});
            expect(scope.userName).toEqual('username');
        });
    });
});
