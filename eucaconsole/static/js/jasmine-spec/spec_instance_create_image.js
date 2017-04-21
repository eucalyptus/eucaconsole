/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
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
        template = template.replace(/<link/g, "<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("should set initial value of expanded to false", function() {
            expect(scope.expanded).toBe(false);
        });

        it("should set initial value of name to empty string", function() {
            expect(scope.name).toEqual('');
        });

        it("should set initial value of bucketName to empty string", function() {
            expect(scope.bucketName).toEqual('');
        });

        it("should set initial value of s3_prefix to 'image'", function() {
            expect(scope.s3_prefix).toEqual('image');
        });

        it("should set initial value of s3BucketError to false", function() {
            expect(scope.s3BucketError).toBe(false);
        });

        it("should set initial value of s3PrefixError to false", function() {
            expect(scope.s3PrefixError).toBe(false);
        });

        it("should set initial value of isNotValid to true", function() {
            expect(scope.isNotValid).toBe(true);
        });
    });

    describe("#checkRequiredInput", function() {

        it("should call validateS3BucketInput() when checkRequiredInput() is called", function() {
            spyOn(scope, 'validateS3BucketInput');
            scope.checkRequiredInput();
            expect(scope.validateS3BucketInput).toHaveBeenCalled();
        });

        it("should call validateS3PrefixInput() when checkRequiredInput() is called", function() {
            spyOn(scope, 'validateS3PrefixInput');
            scope.checkRequiredInput();
            expect(scope.validateS3PrefixInput).toHaveBeenCalled();
        });

        it("should set isNotValid to true if name is empty", function() {
            scope.name = '';
            scope.checkRequiredInput();
            expect(scope.isNotValid).toBe(true);
        });

        it("should set isNotValid to true if bucketName is empty", function() {
            scope.bucketName = '';
            scope.checkRequiredInput();
            expect(scope.isNotValid).toBe(true);
        });

        it("Should set isNotValid to true if s3_prefix is empty", function() {
            scope.s3_prefix = '';
            scope.checkRequiredInput();
            expect(scope.isNotValid).toBe(true);
        });
    });
});
