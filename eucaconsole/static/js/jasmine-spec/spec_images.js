/**
 * @fileOverview Jasmine Unittest for Images JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("ImagesPage", function() {

    beforeEach(angular.mock.module('ImagesPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('ImagesCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/images/images.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of imageID is empty", function() {
            expect(scope.imageID).toEqual('');
        });

        it("Initial value of disabledExplanationVisible is false", function() {
            expect(scope.disabledExplanationVisible).not.toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should set imagesUrl when initController() is called and snapshot_images_json_url JSON is set", function() {
            scope.initController('{"snapshot_images_json_url": "url"}');
            expect(scope.imagesUrl).toEqual('url');
        });

        it("Should call setInitialOwner() when initController() is called and cloud_type is aws", function() {
            spyOn(scope, 'setInitialOwner');
            scope.initController('{"cloud_type": "aws"}');
            expect(scope.setInitialOwner).toHaveBeenCalled();
        });
    });
});
