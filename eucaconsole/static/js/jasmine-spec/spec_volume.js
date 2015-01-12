/**
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
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of transitionalStates[0] is creating", function() {
            expect(scope.transitionalStates[0]).toEqual('creating');
        });

        it("Initial value of transitionalStates[1] is deleting", function() {
            expect(scope.transitionalStates[1]).toEqual('deleting');
        });

        it("Initial value of transitionalStates[2] is attaching", function() {
            expect(scope.transitionalStates[2]).toEqual('attaching');
        });

        it("Initial value of transitionalStates[3] is detaching", function() {
            expect(scope.transitionalStates[3]).toEqual('detaching');
        });

        it("Initial value of volumeStatus is empty", function() {
            expect(scope.volumeStatus).toEqual('');
        });

        it("Initial value of volumeAttachStatus is empty", function() {
            expect(scope.volumeAttachStatus).toEqual('');
        });

        it("Initial value of snapshotId is empty", function() {
            expect(scope.snapshotId).toEqual('');
        });

        it("Initial value of instanceId is empty", function() {
            expect(scope.instanceId).toEqual('');
        });

        it("Initial value of isNotValid is true", function() {
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Initial value of isNotChanged is true", function() {
            expect(scope.isNotChanged).toBeTruthy();
        });

        it("Initial value of isSubmitted is false", function() {
            expect(scope.isSubmitted).not.toBeTruthy();
        });

        it("Initial value of isUpdating is false", function() {
            expect(scope.isUpdating).not.toBeTruthy();
        });

        it("Initial value of fromSnapshot is false", function() {
            expect(scope.fromSnapshot).not.toBeTruthy();
        });

        it("Initial value of volumeSize is 1", function() {
            expect(scope.volumeSize).toEqual(1);
        });

        it("Initial value of snapshotSize is 1", function() {
            expect(scope.snapshotSize).toEqual(1);
        });
    });

    describe("Function initController() Test", function() {

        it("Should call initAvaliZoneChoice() when initController() is called", function() {
            spyOn(scope, 'initAvailZoneChoice');
            scope.initController('{}');
            expect(scope.initAvailZoneChoice).toHaveBeenCalled();
        });
    });
});
