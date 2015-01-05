/**
 * @fileOverview Jasmine Unittest for IAM Bucket Contents JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("BucketContentsPage", function() {

    beforeEach(angular.mock.module('BucketContentsPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('BucketContentsCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/buckets/bucket_contents.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of bucketName is empty", function() {
            expect(scope.bucketName).toEqual('');
        });

        it("Initial value of prefix is empty", function() {
            expect(scope.prefix).toEqual('');
        });

        it("Initial value of folder is empty", function() {
            expect(scope.folder).toEqual('');
        });

        it("Initial value of obj_key is empty", function() {
            expect(scope.obj_key).toEqual('');
        });

        it("Initial value of deletingAll is false", function() {
            expect(scope.deletingAll).not.toBeTruthy();
        });

        it("Initial value of copyingAll is false", function() {
            expect(scope.copyingAll).not.toBeTruthy();
        });

        it("Initial value of progress is 0", function() {
            expect(scope.progress).toEqual(0);
        });

        it("Initial value of total is 0", function() {
            expect(scope.total).toEqual(0);
        });
        it("Initial value of chunkSize is 10", function() {

            expect(scope.chunkSize).toEqual(10);
        });
    });

    describe("Function initController() Test", function() {

        it("Should set bucketName when initController() is called and bucket_name JSON is set", function() {
            scope.initController('{"bucket_name": "bucket"}');
            expect(scope.bucketName).toEqual('bucket');
        });

        it("Should call updatePasteValues() when initController() is called", function() {
            spyOn(scope, 'updatePasteValues');
            scope.initController('{}');
            expect(scope.updatePasteValues).toHaveBeenCalled();
        });
    });
});
