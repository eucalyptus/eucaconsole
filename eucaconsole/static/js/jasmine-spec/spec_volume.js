/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Jasmine Unittest for Volume JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("VolumePage", function() {

    beforeEach(angular.mock.module('VolumePage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('VolumePageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/volumes/volume_view.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/<link/g, "<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("should set initial value of transitionalStates[0] to 'creating'", function() {
            expect(scope.transitionalStates[0]).toEqual('creating');
        });

        it("should set initial value of transitionalStates[1] to 'deleting'", function() {
            expect(scope.transitionalStates[1]).toEqual('deleting');
        });

        it("should set initial value of transitionalStates[2] to 'attaching'", function() {
            expect(scope.transitionalStates[2]).toEqual('attaching');
        });

        it("should set initial value of transitionalStates[3] to 'detaching'", function() {
            expect(scope.transitionalStates[3]).toEqual('detaching');
        });

        it("should set initial value of volumeStatus to empty string", function() {
            expect(scope.volumeStatus).toEqual('');
        });

        it("should set initial value of volumeAttachStatus to empty string", function() {
            expect(scope.volumeAttachStatus).toEqual('');
        });

        it("should set initial value of snapshotId to empty string", function() {
            expect(scope.snapshotId).toEqual('');
        });

        it("should set initial value of instanceId to empty string", function() {
            expect(scope.instanceId).toEqual('');
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

        it("should set initial value of fromSnapshot to false", function() {
            expect(scope.fromSnapshot).toBe(false);
        });

        it("should set initial value of volumeSize to 1", function() {
            expect(scope.volumeSize).toEqual(1);
        });

        it("Initial value of snapshotSize is 1", function() {
            expect(scope.snapshotSize).toEqual(1);
        });
    });

    describe("#initController", function() {

        it("should call initAvaliZoneChoice() when initController() is called", function() {
            spyOn(scope, 'initAvailZoneChoice');
            scope.initController('{}');
            expect(scope.initAvailZoneChoice).toHaveBeenCalled();
        });
    });
});
