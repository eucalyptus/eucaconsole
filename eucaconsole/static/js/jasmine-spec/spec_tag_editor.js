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
            scope.isTagNotComplete = false;
            scope.checkRequiredInput(); 
            expect(scope.isTagNotComplete).toBeTruthy();
        });

        it("Should invalid input when newTagValue is empty", function() {
            scope.newTagValue = '';
            scope.isTagNotComplete = false;
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
            scope.isTagNotComplete = false;
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: 'myDupKey', value: '3'}];
            scope.checkRequiredInput(); 
            expect(scope.isTagNotComplete).toBeTruthy();
        });

        it("Should invalid input when tag-name-input-div element contains error class", function() {
            scope.newTagKey = 'myKey';
            scope.newTagValue = 'myValue';
            scope.isTagNotComplete = false;
            setFixtures('<div id="tag-name-input-div" class="error"></div>');
            scope.checkRequiredInput(); 
            expect(scope.isTagNotComplete).toBeTruthy();
        });

        it("Should invalid input when tag-value-input-div element contains error class", function() {
            scope.newTagKey = 'myKey';
            scope.newTagValue = 'myValue';
            scope.isTagNotComplete = false;
            setFixtures('<div id="tag-value-input-div" class="error"></div>');
            scope.checkRequiredInput(); 
            expect(scope.isTagNotComplete).toBeTruthy();
        });

        it("Should validate input when there is no dup key or value and no error class", function() {
            scope.newTagKey = 'myKey';
            scope.newTagValue = 'myValue';
            scope.tagsArray = [{name: '1', value: '1'}];
            scope.isTagNotComplete = true;
            setFixtures('<div id="tag-name-input-div"></div><div id="tag-value-input-div"></div>');
            scope.checkRequiredInput(); 
            expect(scope.isTagNotComplete).not.toBeTruthy();
        });
    });

    describe("Function checkDuplicatedTagKey() Test", function() {

        beforeEach(function() {
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: 'myDupKey', value: '3'}];
        });

        it("The value of existsTagKey is true when newTagKey already exists", function() {
            scope.newTagKey = 'myDupKey';
            scope.checkDuplicatedTagKey(); 
            expect(scope.existsTagKey).toBeTruthy();
        });

        it("The value of tagKeyClass is 'error' when newTagKey already exists", function() {
            scope.newTagKey = 'myDupKey';
            scope.checkDuplicatedTagKey(); 
            expect(scope.tagKeyClass).toBe('error');
        });

        it("The value of existsTagKey is false when there is no dup key", function() {
            scope.newTagKey = 'myKey';
            scope.checkDuplicatedTagKey(); 
            expect(scope.existsTagKey).not.toBeTruthy();
        });

        it("The value of tagKeyClass is empty when there is no dup key", function() {
            scope.newTagKey = 'myKey';
            scope.checkDuplicatedTagKey(); 
            expect(scope.tagKeyClass).toBe('');
        });
    });

    describe("Function isNameTagIncluded() Test", function() {

        it("Should return true when tagsArray contains an item whose name is 'Name'", function() {
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: 'Name', value: '3'}];
            var returnValue = scope.isNameTagIncluded(); 
            expect(returnValue).toBeTruthy();
        });

        it("Should return false when tagsArray does not contain an item whose name is 'Name'", function() {
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: '3', value: '3'}];
            var returnValue = scope.isNameTagIncluded(); 
            expect(returnValue).not.toBeTruthy();
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

    describe("Function updateTagCount() Test", function() {

        it("Should update tagCount to the length of tagsArray", function() {
            scope.tagCount = 0; 
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: 'Name', value: 'myName'}];
            scope.updateTagCount(); 
            expect(scope.tagCount).toBe(3);
        });

        it("Should update tagCount to the length of tagsArray + 1 if the name input field is included in the page's form", function() {
            scope.tagCount = 0; 
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: '3', value: '3'}];
            setFixtures('<input id="name" value="myName"</input>');
            scope.updateTagCount(); 
            expect(scope.tagCount).toBe(4);
        });

        it("Should not update tagCount to the length of tagsArray + 1 if the name input field is not included in the page's form", function() {
            scope.tagCount = 0; 
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: '3', value: '3'}];
            scope.updateTagCount(); 
            expect(scope.tagCount).toBe(3);
        });

        it("Should not update tagCount to the length of tagsArray + 1 on the security group detail page", function() {
            scope.tagCount = 0; 
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: '3', value: '3'}];
            setFixtures('<form id="security-group-detail-form"><input id="name" value="myName"></input></form>');
            scope.updateTagCount(); 
            expect(scope.tagCount).toBe(3);
        });

        it("Should update tagCount to the length of tagsArray + 1 on the launch instance wizard if a name is entered", function() {
            scope.tagCount = 0; 
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: '3', value: '3'}];
            setFixtures('<form id="launch-instance-form"><input class="name" value="myName"></input></form>');
            scope.updateTagCount(); 
            expect(scope.tagCount).toBe(4);
        });

        it("Should not update tagCount to the length of tagsArray + 1 on the launch instance wizard if no name is entered", function() {
            scope.tagCount = 0; 
            scope.tagsArray = [{name: '1', value: '1'},
                               {name: '2', value: '2'},
                               {name: '3', value: '3'}];
            setFixtures('<form id="launch-instance-form"></form>');
            scope.updateTagCount(); 
            expect(scope.tagCount).toBe(3);
        });
    });
});
