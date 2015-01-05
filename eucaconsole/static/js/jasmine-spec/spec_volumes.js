/**
 * @fileOverview Jasmine Unittest for Volumes JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("VolumesPage", function() {

    beforeEach(angular.mock.module('VolumesPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('VolumesCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/volumes/volumes.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of volumeID is empty", function() {
            expect(scope.volumeID).toEqual('');
        });

        it("Initial value of volumeName is empty", function() {
            expect(scope.volumeName).toEqual('');
        });

        it("Initial value of volumeZone is empty", function() {
            expect(scope.volumeZone).toEqual('');
        });

        it("Initial value of instanceName is empty", function() {
            expect(scope.instanceName).toEqual('');
        });

        it("Initial value of instancesByZone is empty", function() {
            expect(scope.instancesByZone).toEqual('');
        });
    });

    describe("Function initPage() Test", function() {

        it("Should set instanceByZone when initPage() is called", function() {
            scope.initPage('zone');
            expect(scope.instancesByZone).toEqual('zone');
        });
    });

    describe("Function revealModal() Test", function() {

        it("Should set volumeID when revealModal() is called", function() {
            scope.revealModal('a', {id: "v-12345678"});
            expect(scope.volumeID).toEqual('v-12345678');
        });

        it("Should set volumeName when revealModal() is called", function() {
            scope.revealModal('a', {name: "vol"});
            expect(scope.volumeName).toEqual('vol');
        });

        it("Should set instanceName when revealModal() is called and action is detach", function() {
            scope.revealModal('detach', {instance_name: "inst"});
            expect(scope.instanceName).toEqual('inst');
        });
    });

    describe("Function detachModal() Test", function() {

        it("Should set volumeID when detachModal() is called", function() {
            scope.detachModal({id: "v-12345678"}, 'url');
            expect(scope.volumeID).toEqual('v-12345678');
        });

        it("Should set instanceName when revealModal() is called", function() {
            scope.detachModal({instance_name: "inst"}, 'url');
            expect(scope.instanceName).toEqual('inst');
        });
    });
});
