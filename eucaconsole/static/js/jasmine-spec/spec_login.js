/**
 * @fileOverview Jasmine Unittest for Login JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("LoginPage", function() {

    beforeEach(angular.mock.module('LoginPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('LoginPageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/login.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of showHttpsWarning is false", function() {
            expect(scope.showHttpsWarning).not.toBeTruthy();
        });

        it("Initial value of isLoggingIn is false", function() {
            expect(scope.isLoggingIn).not.toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should call prefillForms() when initController() is called", function() {
            spyOn(scope, 'prefillForms');
            scope.initController('{"account": "acct", "username": "user"}');
            expect(scope.prefillForms).toHaveBeenCalled();
        });
    });
});
