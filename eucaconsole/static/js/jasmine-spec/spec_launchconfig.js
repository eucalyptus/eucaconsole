/**
 * @fileOverview Jasmine Unittest for LaunchConfig JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("LaunchConfigPage", function() {

    beforeEach(angular.mock.module('LaunchConfigPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('LaunchConfigPageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/launchconfigs/launchconfig_view.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of launchConfigInUse is undefined", function() {
            expect(scope.launchConfigInUse).toEqual(undefined);
        });

        it("Initial value of hasImage is undefined", function() {
            expect(scope.hasImage).toEqual(undefined);
        });
    });

    describe("Function initController() Test", function() {

        it("Should set launchConfigInUse when initController() is called and in_use JSON is passed", function() {
            scope.initController('{"in_use": "lc-12345678"}');
            expect(scope.launchConfigInUse).toEqual("lc-12345678");
        });

        it("Should set hasImage when initController() is called and has_image JSON is passed", function() {
            scope.initController('{"has_image": "True"}');
            expect(scope.hasImage).toEqual("True");
        });

        it("Should call setWatch() when initController() is called", function() {
            spyOn(scope, 'setWatch');
            scope.initController('{}');
            expect(scope.setWatch).toHaveBeenCalled();
        });

        it("Should call setFocus() when initController() is called", function() {
            spyOn(scope, 'setFocus');
            scope.initController('{}');
            expect(scope.setFocus).toHaveBeenCalled();
        });

    });
});
