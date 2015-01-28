/**
 * @fileOverview Jasmine Unittest for Groups JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("GroupsPage", function() {

    beforeEach(angular.mock.module('GroupsPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('GroupsCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/groups/groups.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of groupName is empty", function() {
            expect(scope.groupName).toEqual('');
        });

        it("Initial value of groupViewUrl is empty", function() {
            expect(scope.groupViewUrl).toEqual('');
        });
    });

    describe("Function initController() Test", function() {

        it("Should set groupViewUrl when initPage() is called", function() {
            scope.initPage('group');
            expect(scope.groupViewUrl).toEqual('group');
        });
    });
});
