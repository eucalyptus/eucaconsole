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

        it("Should call checkDuplicatedTagKey() when checkRequiredInput() is called", function() {
            spyOn(scope, 'checkDuplicatedTagKey');
            scope.checkRequiredInput(); 
            expect(scope.checkDuplicatedTagKey).toHaveBeenCalled();
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

    describe("Function checkDuplicatedTagKey() Test", function() {

        beforeEach(function() {
            scope.newTagKey = 'myDupKey';
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: 'myDupKey', value: '3'}];
        });

        it("The value of existsTagKey is true when newTagKey already exists", function() {
            scope.checkDuplicatedTagKey(); 
            expect(scope.existsTagKey).toBeTruthy();
        });

        it("The value of tagKeyClass is 'error' when newTagKey already exists", function() {
            scope.checkDuplicatedTagKey(); 
            expect(scope.tagKeyClass).toBe('error');
        });
    });

    describe("Function isNameTagIncluded() Test", function() {

        beforeEach(function() {
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: 'Name', value: '3'}];
        });

        it("Should return true when tagsArray contains an item whose name is 'Name'", function() {
            var returnValue = scope.isNameTagIncluded(); 
            expect(returnValue).toBeTruthy();
        });
    });

    describe("Function updateVisibleTagsCount() Test", function() {

        beforeEach(function() {
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: '3', value: '3'}];
        });

        it("Should update visiableTagsCount to the length of tagsArray if showNameTag is true", function() {
            scope.showNameTag = true;
            scope.updateVisibleTagsCount(); 
            expect(scope.visibleTagsCount).toBe(3);
        });

        it("Should update visiableTagsCount to the length of tagsArray if showNameTag is false and the array does not include an item whose name is 'Name'", function() {
            scope.showNameTag = false;
            scope.updateVisibleTagsCount(); 
            expect(scope.visibleTagsCount).toBe(3);
        });

        it("Should update visiableTagsCount to the length of tagsArray while excluding an item whose name is 'Name' if showNameTag is false", function() {
            scope.showNameTag = false;
            scope.tagsArray.push({name: 'Name', value: '4'});
            scope.updateVisibleTagsCount(); 
            expect(scope.visibleTagsCount).toBe(3);
        });

        it("Should update visiableTagsCount to the length of tagsArray while including an item whose name is 'Name' if showNameTag is true", function() {
            scope.showNameTag = true;
            scope.tagsArray.push({name: 'Name', value: '4'});
            scope.updateVisibleTagsCount(); 
            expect(scope.visibleTagsCount).toBe(4);
        });
    });
});
