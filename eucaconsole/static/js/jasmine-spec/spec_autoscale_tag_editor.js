/**
 * @fileOverview Jasmine Unittest for AutoScale Tag Editor JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("AutoScaleTagEditor", function() {

    beforeEach(angular.mock.module('AutoScaleTagEditor'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('AutoScaleTagEditorCtrl', {
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

        it("Should invalid input when newTagKey already exists", function() {
            scope.newTagKey = 'myDupKey';
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: 'myDupKey', value: '3'}];
            scope.checkRequiredInput(); 
            expect(scope.isTagNotComplete).toBeTruthy();
        });
    });
});
