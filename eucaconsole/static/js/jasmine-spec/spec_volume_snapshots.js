/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview Jasmine Unittest for Volume Snapshots JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("VolumeSnapshots", function() {

    beforeEach(angular.mock.module('VolumeSnapshots'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('VolumeSnapshotsCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/volumes/volume_snapshots.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/<link/g, "<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("should set initial value of loading to false", function() {
            expect(scope.loading).toBe(false);
        });

        it("should set initial value of jsonEndpoint to empty string", function() {
            expect(scope.jsonEndpoint).toEqual('');
        });

        it("should set initial value of initialLoading to true", function() {
            expect(scope.initialLoading).toBe(true);
        });

        it("should set initial value of snapshotID to empty string", function() {
            expect(scope.snapshotID).toEqual('');
        });

        it("should set initial value of snapshotName to empty string", function() {
            expect(scope.snapshotName).toEqual('');
        });

        it("should set initial value of imagesURL to empty string", function() {
            expect(scope.imagesURL).toEqual('');
        });

        it("should set initial value of images to undefined", function() {
            expect(scope.images).toEqual(undefined);
        });
    });

    describe("#initController", function() {

        it("should set jsonEndpoint when initController() is called", function() {
            scope.initController('a', 'b');
            expect(scope.jsonEndpoint).toEqual('a');
        });

        it("should set imagesURL when initController() is called", function() {
            scope.initController('a', 'b');
            expect(scope.imagesURL).toEqual('b');
        });

        it("should call getVolumeSnapshots() when initController() is called", function() {
            spyOn(scope, 'getVolumeSnapshots');
            scope.initController('a', 'b');
            expect(scope.getVolumeSnapshots).toHaveBeenCalled();
        });

        it("should call setFocus() when initController() is called", function() {
            spyOn(scope, 'setFocus');
            scope.initController('a', 'b');
            expect(scope.setFocus).toHaveBeenCalled();
        });
    });
});
