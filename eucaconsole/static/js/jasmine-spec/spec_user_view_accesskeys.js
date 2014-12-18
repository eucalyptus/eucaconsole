/**
 * @fileOverview Jasmine Unittest for IAM UserView AccessKeys JS 
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
        ctrl = $controller('UserAccessKeysCtrl', {
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

        it("Initial value of jsonEndpoint is empty", function() {
            expect(scope.jsonEndpoint).toEqual('');
        });

        it("Initial value of jsonItemsEndpoint is empty", function() {
            expect(scope.jsonItemsEndpoint).toEqual('');
        });

        it("Initial value of getFileEndpoint is empty", function() {
            expect(scope.getFileEndpoint).toEqual('');
        });

        it("Initial value of itemsLoading is true", function() {
            expect(scope.itemsLoading).toBeTruthy();
        });

        it("Initial value of userWithKey is empty", function() {
            expect(scope.userWithKey).toEqual('');
        });

        it("Initial value of keyToDelete is empty", function() {
            expect(scope.keyToDelete).toEqual('');
        });
    });

    describe("Function initController() Test", function() {

        it("Should set jsonEndpoint when initController() is called", function() {
            scope.initController('a', 'b', 'c');
            expect(scope.jsonEndpoint).toEqual('a');
        });

        it("Should call getItems() when initController() is called", function() {
            spyOn(scope, 'getItems');
            scope.initController('a', 'b', 'c');
            expect(scope.getItems).toHaveBeenCalled();
        });
    });
});
