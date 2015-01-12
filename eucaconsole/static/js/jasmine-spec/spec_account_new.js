/**
 * @fileOverview Jasmine Unittest for IAM Account New JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("AccountPage", function() {

    beforeEach(angular.mock.module('AccountPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('AccountPageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/accounts/account_new.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of accountName is empty", function() {
            expect(scope.accountName).toEqual('');
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
            scope.initController('a', 'b', 'c');
            expect(scope.submitEndpoint).toEqual('a');
        });

        it("Should call setWatch() when initController() is called", function() {
            spyOn(scope, 'setWatch');
            scope.initController('a', 'b', 'c');
            expect(scope.setWatch).toHaveBeenCalled();
        });
    });
});
