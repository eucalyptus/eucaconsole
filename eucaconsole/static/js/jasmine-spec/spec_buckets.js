/**
 * @fileOverview Jasmine Unittest for Buckets JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("BucketsPage", function() {

    beforeEach(angular.mock.module('BucketsPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('BucketsCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/buckets/buckets.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of bucketName is empty", function() {
            expect(scope.bucketName).toEqual('');
        });

        it("Initial value of updateVersioningAction is empty", function() {
            expect(scope.updateVersioningAction).toEqual('');
        });

        it("Initial value of copyingAll is false", function() {
            expect(scope.copyingAll).not.toBeTruthy();
        });

        it("Initial value of chunkSize is 10", function() {
            expect(scope.chunkSize).toEqual(10);
        });

        it("Initial value of hasCopyItem is false", function() {
            expect(scope.hasCopyItem).not.toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should set bucketObjectsCountUrl when initController() is called and bucket_objects_count_url JSON is set", function() {
            scope.initController('{"bucket_objects_count_url": "url"}');
            expect(scope.bucketObjectsCountUrl).toEqual('url');
        });

        it("Should call updatePasteValues() when initController() is called", function() {
            spyOn(scope, 'updatePasteValues');
            scope.initController('{}');
            expect(scope.updatePasteValues).toHaveBeenCalled();
        });
    });
});
