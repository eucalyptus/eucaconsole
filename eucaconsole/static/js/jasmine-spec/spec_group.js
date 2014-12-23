/**
 * @fileOverview Jasmine Unittest for IAM Group JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("GroupPage", function() {

    beforeEach(angular.mock.module('GroupPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('GroupPageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/groups/group_view.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of groupName is empty", function() {
            expect(scope.groupName).toEqual('');
        });

        it("Initial value of isSubmitted is false", function() {
            expect(scope.isSubmitted).not.toBeTruthy();
        });

        it("Initial value of isNotChanged is true", function() {
            expect(scope.isNotChanged).toBeTruthy();
        });

        it("Initial value of pendingModalID is empty", function() {
            expect(scope.pendingModalID).toEqual('');
        });
    });

    describe("Function initController() Test", function() {

        it("Should set groupName when initController() is called and group_name JSON is passed", function() {
            scope.initController('{"group_name": "group"}');
            expect(scope.groupName).toEqual('group');
        });

        it("Should set groupUsers when initController() is called and group_users JSON is passed", function() {
            scope.initController('{"group_users": "users"}');
            expect(scope.groupUsers).toEqual('users');
        });

        it("Should set allUsers when initController() is called and all_users JSON is passed", function() {
            scope.initController('{"all_users": "all-users"}');
            expect(scope.allUsers).toEqual('all-users');
        });

        it("Should call setWatch() when initController() is called", function() {
            spyOn(scope, 'setWatch');
            scope.initController('{}');
            expect(scope.setWatch).toHaveBeenCalled();
        });
    });
});
