/**
 * @fileOverview Jasmine Unittest for Instance Create Image JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("InstanceCreateImage", function() {

    beforeEach(angular.mock.module('InstanceCreateImage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('InstanceCreateImageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/instances/instance_create_image.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of expanded is false", function() {
            expect(scope.expanded).not.toBeTruthy();
        });

        it("Initial value of name is empty", function() {
            expect(scope.name).toEqual('');
        });

        it("Initial value of s3_bucket is empty", function() {
            expect(scope.s3_bucket).toEqual('');
        });

        it("Initial value of s3_prefix is image", function() {
            expect(scope.s3_prefix).toEqual('image');
        });

        it("Initial value of s3BucketError is false", function() {
            expect(scope.s3BucketError).not.toBeTruthy();
        });

        it("Initial value of s3PrefixError is false", function() {
            expect(scope.s3PrefixError).not.toBeTruthy();
        });

        it("Initial value of isNotValid is true", function() {
            expect(scope.isNotValid).toBeTruthy();
        });
    });

    describe("Function checkRequiredInput() Test", function() {

        it("Should call validateS3BucketInput() when checkRequiredInput() is called", function() {
            spyOn(scope, 'validateS3BucketInput');
            scope.checkRequiredInput();
            expect(scope.validateS3BucketInput).toHaveBeenCalled();
        });

        it("Should call validateS3PrefixInput() when checkRequiredInput() is called", function() {
            spyOn(scope, 'validateS3PrefixInput');
            scope.checkRequiredInput();
            expect(scope.validateS3PrefixInput).toHaveBeenCalled();
        });

        it("Should invalid input if name is empty", function() {
            scope.name = '';
            scope.checkRequiredInput();
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input if s3_bucket is empty", function() {
            scope.s3_bucket = '';
            scope.checkRequiredInput();
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input if s3_prefix is empty", function() {
            scope.s3_prefix = '';
            scope.checkRequiredInput();
            expect(scope.isNotValid).toBeTruthy();
        });
    });
});
