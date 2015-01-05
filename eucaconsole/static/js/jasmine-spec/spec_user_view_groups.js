/**
 * @fileOverview Jasmine Unittest for IAM User Groups JS 
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
        ctrl = $controller('UserGroupsCtrl', {
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

        it("Initial value of addEndpoint is empty", function() {
            expect(scope.addEndpoint).toEqual('');
        });

        it("Initial value of removeEndpoint is empty", function() {
            expect(scope.removeEndpoint).toEqual('');
        });

        it("Initial value of jsonItemsEndpoint is empty", function() {
            expect(scope.jsonItemsEndpoint).toEqual('');
        });

        it("Initial value of groupName is empty", function() {
            expect(scope.groupName).toEqual('');
        });

        it("Initial value of isGroupNotSelected is true", function() {
            expect(scope.isGroupNotSelected).toBeTruthy();
        });

        it("Initial value of itemsLoading is true", function() {
            expect(scope.itemsLoading).toBeTruthy();
        });

        it("Initial value of policyName is empty", function() {
            expect(scope.policyName).toEqual('');
        });

        it("Initial value of policyJson is empty", function() {
            expect(scope.policyJson).toEqual('');
        });

        it("Initial value of noGroupsDefined is true", function() {
            expect(scope.noGroupsDefined).not.toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should set addEndpoint when initController() is called", function() {
            scope.initController('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h');
            expect(scope.addEndpoint).toEqual('a');
        });

        it("Should call getItems() when initController() is called", function() {
            spyOn(scope, 'getItems');
            scope.initController('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h');
            expect(scope.getItems).toHaveBeenCalled();
        });
    });
});
