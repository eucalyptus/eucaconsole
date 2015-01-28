/**
 * @fileOverview Jasmine Unittest for IAM Bucket Upload JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("UploadFilePage", function() {

    beforeEach(angular.mock.module('UploadFilePage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('UploadFilePageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/buckets/bucket_upload.pt'];
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

        it("Initial value of isNotValid is true", function() {
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Initial value of loading is false", function() {
            expect(scope.loading).not.toBeTruthy();
        });

        it("Initial value of progress is 0", function() {
            expect(scope.progress).toEqual(0);
        });

        it("Initial value of total is 0", function() {
            expect(scope.total).toEqual(0);
        });
    });

    describe("Function initController() Test", function() {

        it("Should set uploadUrl when initController() is called", function() {
            scope.initController('a', 'b');
            expect(scope.uploadUrl).toEqual('a');
        });

        it("Should set bucketUrl when initController() is called", function() {
            scope.initController('a', 'b');
            expect(scope.bucketUrl).toEqual('b');
        });

        it("Should call handleUnsavedChanges() when initController() is called", function() {
            spyOn(scope, 'handleUnsavedChanges');
            scope.initController('a', 'b');
            expect(scope.handleUnsavedChanges).toHaveBeenCalled();
        });
    });
});
