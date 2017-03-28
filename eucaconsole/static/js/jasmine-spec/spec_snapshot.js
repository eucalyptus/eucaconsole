/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Jasmine Unittest for Snapshot JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("SnapshotPage", function() {

    beforeEach(angular.mock.module('SnapshotPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('SnapshotPageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/snapshots/snapshot_view.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/<link/g, "<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("should set initial value of transitionalStates[0] to 'pending'", function() {
            expect(scope.transitionalStates[0]).toEqual('pending');
        });

        it("should set initial value of transitionalStates[1] to 'deleting'", function() {
            expect(scope.transitionalStates[1]).toEqual('deleting');
        });

        it("should set initial value of snapshotStatus to empty string", function() {
            expect(scope.snapshotStatus).toEqual('');
        });

        it("should set initial value of snapshotProgress to empty string", function() {
            expect(scope.snapshotProgress).toEqual('');
        });

        it("should set initial value of isNotValid to true", function() {
            expect(scope.isNotValid).toBe(true);
        });

        it("should set initial value of isNotChanged to true", function() {
            expect(scope.isNotChanged).toBe(true);
        });

        it("should set initial value of isSubmitted to false", function() {
            expect(scope.isSubmitted).toBe(false);
        });

        it("should set initial value of isUpdating to false", function() {
            expect(scope.isUpdating).toBe(false);
        });

        it("should set initial value of volumeID to empty string", function() {
            expect(scope.volumeID).toEqual('');
        });

        it("should set initial value of imagesURL to empty string", function() {
            expect(scope.imagesURL).toEqual('');
        });

        it("should set initial value of images to undefined", function() {
            expect(scope.images).toEqual(undefined);
        });

        it("should set initial value of pendingModalID to empty string", function() {
            expect(scope.pendingModalID).toEqual('');
        });
    });

    describe("#initController", function() {

        it("should call getSnapshotState() when initController() is called and snapshotStatusEndpoint is set", function() {
            spyOn(scope, 'getSnapshotState');
            scope.initController('{"snapshot_status_json_url": "/snapshots/sn-12345678/status/json"}');
            expect(scope.getSnapshotState).toHaveBeenCalled();
        });
    });

    describe("#inProgress", function() {

        it("should set inProgress to true when snapshot is 25% complete", function () {
            expect(scope.inProgress('25%')).toBe(true);
        });

        it("should set inProgress to false when snapshot is 100% complete", function () {
            expect(scope.inProgress('100%')).toBe(false);
        });
    });

    describe("#isTransitional", function() {

        it("should set isTransitional to true when in 'pending' state", function () {
            expect(scope.isTransitional('pending')).toBe(true);
        });

        it("should set isTransitional to true when in 'deleting' state", function () {
            expect(scope.isTransitional('deleting')).toBe(true);
        });

        it("should set isTransitional to false when in 'completed' state", function () {
            expect(scope.isTransitional('completed')).toBe(false);
        });
    });

});
