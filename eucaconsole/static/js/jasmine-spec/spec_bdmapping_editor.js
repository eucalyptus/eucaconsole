/**
 * @fileOverview Jasmine Unittest for Block Device Mapping Editor JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("BlockDeviceMappingEditor", function() {

    beforeEach(angular.mock.module('BlockDeviceMappingEditor'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('BlockDeviceMappingEditorCtrl', {
            $scope: scope
        });
    }));

    describe("Initial Values Test", function() {

        it("Initial value of newVolumeType is EBS", function() {
            scope.setInitialNewValues();
            expect(scope.newVolumeType).toEqual('EBS');
        });

        it("Initial value of virtualName is empty", function() {
            scope.setInitialNewValues();
            expect(scope.virtualName).toEqual('');
        });

        it("Initial value of newSnapshotID is empty", function() {
            scope.setInitialNewValues();
            expect(scope.newSnapshotID).toEqual('');
        });

        it("Initial value of newMappingPath is empty", function() {
            scope.setInitialNewValues();
            expect(scope.newMappingPath).toEqual('');
        });

        it("Initial value of newSize is 2", function() {
            scope.setInitialNewValues();
            expect(scope.newSize).toEqual('2');
        });

        it("Initial value of newDOT is true", function() {
            scope.setInitialNewValues();
            expect(scope.newDOT).toBeTruthy();
        });
    });

    describe("Function checkValidInput() Test", function() {

        it("Should invalid input when newMappingPath is empty", function() {
            scope.isNotValid = false;
            scope.newMappingPath = '';
            scope.checkValidInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when newSize is empty", function() {
            scope.isNotValid = false;
            scope.newSize = '';
            scope.checkValidInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });
    });
});
