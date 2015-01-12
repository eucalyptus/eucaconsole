/**
 * @fileOverview Jasmine Unittest for Accounts JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("AccountsPage", function() {

    beforeEach(angular.mock.module('AccountsPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('AccountsCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/accounts/accounts.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of accountName is empty", function() {
            expect(scope.accountName).toEqual('');
        });

        it("Initial value of accountViewUrl is empty", function() {
            expect(scope.accountViewUrl).toEqual('');
        });

        it("Initial value of accountSummaryUrl is empty", function() {
            expect(scope.accountSummaryUrl).toEqual('');
        });
    });

    describe("Function initPage() Test", function() {

        it("Should set accountViewUrl when initController() is called", function() {
            scope.initPage('a', 'b');
            expect(scope.accountViewUrl).toEqual('a');
        });

        it("Should set accountSummaryUrl when initController() is called", function() {
            scope.initPage('a', 'b');
            expect(scope.accountSummaryUrl).toEqual('b');
        });
    });
});
