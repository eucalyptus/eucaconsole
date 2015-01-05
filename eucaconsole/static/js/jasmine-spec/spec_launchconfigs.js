/**
 * @fileOverview Jasmine Unittest for LaunchConfigs JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("LaunchConfigsPage", function() {

    beforeEach(angular.mock.module('LaunchConfigsPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('LaunchConfigsPageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/launchconfigs/launchconfigs.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of launchConfigName is empty", function() {
            expect(scope.launchConfigName).toEqual('');
        });
    });

    describe("Function revealModal() Test", function() {

        it("Should set launchConfigName when revealModal() is called", function() {
            scope.revealModal('a', {name: "lc"});
            expect(scope.launchConfigName).toEqual('lc');
        });
    });
});
