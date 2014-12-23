/**
 * @fileOverview Jasmine Unittest for Image JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("ImagePage", function() {

    beforeEach(angular.mock.module('ImagePage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('ImagePageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/images/image_view.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of imageState is empty", function() {
            expect(scope.imageState).toEqual('');
        });

        it("Initial value of imageProgess is 0", function() {
            expect(scope.imageProgess).toEqual(0);
        });

        it("Initial value of transitionalStates[0] is pending", function() {
            expect(scope.transitionalStates[0]).toEqual('pending');
        });

        it("Initial value of transitionalStates[1] is storing", function() {
            expect(scope.transitionalStates[1]).toEqual('storing');
        });

        it("Initial value of isAccountNotTyped is true", function() {
            expect(scope.isAccountNotTyped).toBeTruthy();
        });

        it("Initial value of isAccountValid is true", function() {
            expect(scope.isAccountValid).toBeTruthy();
        });

        it("Initial value of isNotChanged is true", function() {
            expect(scope.isNotChanged).toBeTruthy();
        });

        it("Initial value of isSubmitted is false", function() {
            expect(scope.isSubmitted).not.toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should call getImageState() when initController() is called and imageStatusEndpoint is set", function() {
            spyOn(scope, 'getImageState');
            scope.initController('{"image_state_json_url": "/images/emi-12345678/state/json"}');
            expect(scope.getImageState).toHaveBeenCalled();
        });
    });
});
