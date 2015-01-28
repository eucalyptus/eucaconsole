/**
 * @fileOverview Jasmine Unittest for IAM Bucket Details JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("BucketDetailsPage", function() {

    beforeEach(angular.mock.module('BucketDetailsPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('BucketDetailsPageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/buckets/bucket_details.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of isSubmitted is false", function() {
            expect(scope.isSubmitted).not.toBeTruthy();
        });

        it("Initial value of hasChangesToBeSaved is false", function() {
            expect(scope.hasChangesToBeSaved).not.toBeTruthy();
        });

        it("Initial value of objectsCountLoading is true", function() {
            expect(scope.objectsCountLoading).toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should set bucketObjectsCountUrl when initController() is called", function() {
            scope.initController('a');
            expect(scope.bucketObjectsCountUrl).toEqual('a');
        });

        it("Should call handleUnsavedChanges() when initController() is called", function() {
            spyOn(scope, 'handleUnsavedChanges');
            scope.initController('{}');
            expect(scope.handleUnsavedChanges).toHaveBeenCalled();
        });
    });
});
