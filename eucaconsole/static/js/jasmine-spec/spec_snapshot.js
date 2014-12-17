/**
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
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of transitionalStates[0] is pending", function() {
            expect(scope.transitionalStates[0]).toEqual('pending');
        });

        it("Initial value of transitionalStates[1] is deleting", function() {
            expect(scope.transitionalStates[1]).toEqual('deleting');
        });

        it("Initial value of snapshotStatus is empty", function() {
            expect(scope.snapshotStatus).toEqual('');
        });

        it("Initial value of snapshotProgress is empty", function() {
            expect(scope.snapshotProgress).toEqual('');
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

        it("Initial value of volumeID is empty", function() {
            expect(scope.volumeID).toEqual('');
        });

        it("Initial value of imagesURL is empty", function() {
            expect(scope.imagesURL).toEqual('');
        });

        it("Initial value of images is undefined", function() {
            expect(scope.images).toEqual(undefined);
        });

        it("Initial value of pendingModalID is empty", function() {
            expect(scope.pendingModalID).toEqual('');
        });
    });

    describe("Function initController() Test", function() {

        it("Should call getSnapshotState() when initController() is called and snapshotStatusEndpoint is set", function() {
            spyOn(scope, 'getSnapshotState');
            scope.initController('{"snapshot_status_json_url": "/snapshots/sn-12345678/status/json"}');
            expect(scope.getSnapshotState).toHaveBeenCalled();
        });
    });
});
