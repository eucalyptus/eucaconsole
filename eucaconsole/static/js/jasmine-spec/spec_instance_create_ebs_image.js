/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Jasmine Unittest for Instance Create EBS Image JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("InstanceCreateEBSImage", function() {

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

        it("should set initial value of isNotValid to true", function() {
            expect(scope.isNotValid).toBe(true);
        });
    });

    describe("#checkRequiredInput", function() {

        it("should set isNotValid to true if name is empty", function() {
            scope.name = '';
            scope.checkRequiredInput();
            expect(scope.isNotValid).toBe(true);
        });
    });
});
