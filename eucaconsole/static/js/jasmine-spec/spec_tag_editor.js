/**
 * @fileOverview Jasmine Unittest for Tag Editor JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("TagEditor", function() {

    beforeEach(angular.mock.module('TagEditor'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('TagEditorCtrl', {
            $scope: scope
        });
    }));

    describe("Initial Values Test", function() {

        it("Initial value of existsTagKey is false", function() {
            expect(scope.existsTagKey).not.toBeTruthy();
        });

        it("Initial value of newTagKey is empty", function() {
            expect(scope.newTagKey).toEqual('');
        });

        it("Initial value of newTagValue is empty", function() {
            expect(scope.newTagValue).toEqual('');
        });

        it("Initial value of tagKeyClass is empty", function() {
            expect(scope.tagKeyClass).toEqual('');
        });
    });

    describe("Function checkRequiredInput() Test", function() {

        it("Should invalid input when newTagKey is empty", function() {
            scope.newTagKey = '';
            scope.checkRequiredInput(); 
            expect(scope.isTagNotComplete).toBeTruthy();
        });

        it("Should invalid input when newTagValue is empty", function() {
            scope.newTagValue = '';
            scope.checkRequiredInput(); 
            expect(scope.isTagNotComplete).toBeTruthy();
        });

    });
});
