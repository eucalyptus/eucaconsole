/**
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
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of loading is false", function() {
            expect(scope.loading).not.toBeTruthy();
        });

        it("Initial value of jsonEndpoint is empty", function() {
            expect(scope.jsonEndpoint).toEqual('');
        });

        it("Initial value of initialLoading is true", function() {
            expect(scope.initialLoading).toBeTruthy();
        });

        it("Initial value of snapshotID is empty", function() {
            expect(scope.snapshotID).toEqual('');
        });

        it("Initial value of snapshotName is empty", function() {
            expect(scope.snapshotName).toEqual('');
        });

        it("Initial value of imagesURL is empty", function() {
            expect(scope.imagesURL).toEqual('');
        });

        it("Initial value of images is undefined", function() {
            expect(scope.images).toEqual(undefined);
        });
    });

    describe("Function initController() Test", function() {

        it("Should set jsonEndpoint when initController() is called", function() {
            scope.initController('a', 'b');
            expect(scope.jsonEndpoint).toEqual('a');
        });

        it("Should set imagesURL when initController() is called", function() {
            scope.initController('a', 'b');
            expect(scope.imagesURL).toEqual('b');
        });

        it("Should call getVolumeSnapshots() when initController() is called", function() {
            spyOn(scope, 'getVolumeSnapshots');
            scope.initController('a', 'b');
            expect(scope.getVolumeSnapshots).toHaveBeenCalled();
        });
    });
});
