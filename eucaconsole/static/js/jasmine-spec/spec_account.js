/**
 * @fileOverview Jasmine Unittest for IAM Account JS 
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
        var template = window.__html__['templates/accounts/account_view.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of currentTab is general-tab", function() {
            expect(scope.currentTab).toEqual('general-tab');
        });

        it("Initial value of isNotChanged is true", function() {
            expect(scope.isNotChanged).toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should call setWatch() when initController() is called", function() {
            spyOn(scope, 'setWatch');
            scope.initController('{}');
            expect(scope.setWatch).toHaveBeenCalled();
        });
    });
});
