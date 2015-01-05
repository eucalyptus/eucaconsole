/**
 * @fileOverview Jasmine Unittest for Snapshots JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("SnapshotPage", function() {

    beforeEach(angular.mock.module('SnapshotsPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('SnapshotsCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/snapshots/snapshots.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of snapshotID is empty", function() {
            expect(scope.snapshotID).toEqual('');
        });

        it("Initial value of snapshotName is empty", function() {
            expect(scope.snapshotName).toEqual('');
        });
    });

    describe("Function revealModal() Test", function() {

        it("Should set snapshotID when revealModal() is called", function() {
            scope.revealModal('a', {id: "sn-12345678"});
            expect(scope.snapshotID).toEqual('sn-12345678');
        });

        it("Should set snapshotName when revealModal() is called", function() {
            scope.revealModal('a', {name: "snap"});
            expect(scope.snapshotName).toEqual('snap');
        });
    });
});
