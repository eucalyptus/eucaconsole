/**
 * @fileOverview Jasmine Unittest for Keypairs JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("KeypairsPage", function() {

    beforeEach(angular.mock.module('KeypairsPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('KeypairsCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/keypairs/keypairs.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of keypairName is empty", function() {
            expect(scope.keypairName).toEqual('');
        });
    });

    describe("Function revealModal() Test", function() {

        it("Should set keypairName when revealModal() is called", function() {
            scope.revealModal('a', 'b');
            expect(scope.keypairName).toEqual('b');
        });
    });
});
