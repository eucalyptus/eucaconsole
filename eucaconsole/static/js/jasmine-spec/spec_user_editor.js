/**
 * @fileOverview Jasmine Unittest for User Editor JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("UserEditor", function() {

    beforeEach(angular.mock.module('UserEditor'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('UserEditorCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/panels/user_editor.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of isDisabled is true", function() {
            expect(scope.isDisabled).toBeTruthy();
        });

        it("Initial value of newUserName is empty", function() {
            expect(scope.newUserName).toEqual('');
        });
    });

    describe("Function initUsers() Test", function() {

        it("Should call syncUsers() when initUsers() is called", function() {
            spyOn(scope, 'syncUsers');
            scope.initUsers();
            expect(scope.syncUsers).toHaveBeenCalled();
        });
    });

    describe("Function validateUsername() Test", function() {

        it("Should invalid input if newUsername contains special chars other than +=,.@-", function() {
            scope.isDisabled = false;
            scope.newUserName = "newuser&*";
            scope.validateUsername();
            expect(scope.isDisabled).toBeTruthy();
        });

        it("Should invalid input if newUsername is empty", function() {
            scope.isDisabled = false;
            scope.newUserName = '';
            scope.validateUsername();
            expect(scope.isDisabled).toBeTruthy();
        });

        it("Should invalid input if newUsername is more than 64 chars", function() {
            scope.isDisabled = false;
            scope.newUserName = "123456789a123456789b123456789c123456789d123456789e123456789f123456789g";
            scope.validateUsername();
            expect(scope.isDisabled).toBeTruthy();
        });

        it("Should invalid input if newUsername is between 1 and 64 chars and may contain special chars +=,.@-", function() {
            scope.isDisabled = true;
            scope.newUserName = "newuser@newaccount.com+=,.@-";
            scope.validateUsername();
            expect(scope.isDisabled).not.toBeTruthy();
        });
    });
});
