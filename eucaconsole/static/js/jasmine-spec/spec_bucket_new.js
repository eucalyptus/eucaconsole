/**
 * @fileOverview Jasmine Unittest for IAM Bucket New JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("CreateBucketPage", function() {

    beforeEach(angular.mock.module('CreateBucketPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('CreateBucketPageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/buckets/bucket_new.pt'];
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

        it("Initial value of bucketName is empty", function() {
            expect(scope.bucketName).toEqual('');
        });
    });

    describe("Function initController() Test", function() {

        it("Should set bucketName when initController() is called and bucket_name JSON is set", function() {
            scope.initController('{"bucket_name": "bucket"}');
            expect(scope.bucketName).toEqual('bucket');
        });

        it("Should call handleUnsavedChanges() when initController() is called", function() {
            spyOn(scope, 'handleUnsavedChanges');
            scope.initController('{}');
            expect(scope.handleUnsavedChanges).toHaveBeenCalled();
        });
    });
});
