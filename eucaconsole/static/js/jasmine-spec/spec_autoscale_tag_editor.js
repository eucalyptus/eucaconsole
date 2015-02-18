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

    beforeEach(function() {
        var template = window.__html__['templates/panels/autoscale_tag_editor.pt'];
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/<link/g, "<ignore_link"); 
        setFixtures(template);
    });

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

        it("Initial value of tagEditor is undefined", function() {
            expect(scope.tagEditor).toEqual(undefined);
        });

        it("Initial value of tagInputs is undefined", function() {
            expect(scope.tagInputs).toEqual(undefined);
        });

        it("Initial value of tagsTextarea is undefined", function() {
            expect(scope.tagsTextarea).toEqual(undefined);
        });
    });

    describe("Function checkRequiredInput() Test", function() {

        beforeEach(function() {
            scope.isTagNotComplete = false;
        });

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

        it("Should invalid input when autoscale-tag-name-input-div element contains error class", function() {
            scope.newTagKey = 'myKey';
            scope.newTagValue = 'myValue';
            setFixtures('<div id="autoscale-tag-name-input-div" class="error"></div>');
            scope.checkRequiredInput(); 
            expect(scope.isTagNotComplete).toBeTruthy();
        });

        it("Should invalid input when autoscale-tag-value-input-div element contains error class", function() {
            scope.newTagKey = 'myKey';
            scope.newTagValue = 'myValue';
            setFixtures('<div id="autoscale-tag-value-input-div" class="error"></div>');
            scope.checkRequiredInput(); 
            expect(scope.isTagNotComplete).toBeTruthy();
        });

        it("Should valid input when newTagKey and newTagValue are specified and input elements contain no error class", function() {
            scope.newTagKey = 'myKey';
            scope.newTagValue = 'myValue';
            scope.checkRequiredInput(); 
            expect(scope.isTagNotComplete).not.toBeTruthy();
        });
    });

    describe("Function updateTagCount() Test", function() {

        it("Should update tagCount to the length of tagsArray", function() {
            scope.tagCount = 0; 
            scope.tagsArray = [{name: '1', value: 'a', propagate_at_launch: true},
                               {name: '2', value: 'b'},
                               {name: 'Name', value: 'myName'}];
            scope.updateTagCount(); 
            expect(scope.tagCount).toBe(3);
        });
    });

    describe("Function syncTags Test", function() {

        beforeEach(function() {
            scope.initTags('{"tags_list": [{"name": "1", "value": "a", "propagate_at_launch": true},{"name": "2", "value": "b"}, {"name": "3", "value": "c"}]}');
        });

        it("Should update textarea#tags with the string of tagsArray values when syncTags is called", function() {
            scope.syncTags(); 
            expect(scope.tagsTextarea.val()).toBe('[{"name":"1","value":"a","propagate_at_launch":true},{"name":"2","value":"b"},{"name":"3","value":"c"}]');
        });
    });

    describe("Function initTags Test", function() {

        it("Should call syncTags when initTags is called", function() {
            spyOn(scope, 'syncTags');
            scope.initTags('{"tags_list": [{"name": "1", "value": "a", "propagate_at_launch": true},{"name": "2", "value": "b"}, {"name": "3", "value": "c"}]}');
            expect(scope.syncTags).toHaveBeenCalled();
        });

        it("Should call setWatch when initTags is called", function() {
            spyOn(scope, 'setWatch');
            scope.initTags('{"tags_list": [{"name": "1", "value": "a", "propagate_at_launch": true},{"name": "2", "value": "b"}, {"name": "3", "value": "c"}]}');
            expect(scope.setWatch).toHaveBeenCalled();
        });

        it("Should update tagArray when initTags is called with tags option", function() {
            scope.initTags('{"tags_list": [{"name": "1", "value": "a", "propagate_at_launch": true},{"name": "2", "value": "b"}, {"name": "3", "value": "c"}]}');
            expect(scope.tagsArray.length).toBe(3);
            expect(scope.tagsArray[0].name).toBe("1");
            expect(scope.tagsArray[0].value).toBe("a");
            expect(scope.tagsArray[1].name).toBe("2");
            expect(scope.tagsArray[1].value).toBe("b");
            expect(scope.tagsArray[2].name).toBe("3");
            expect(scope.tagsArray[2].value).toBe("c");
        });

        it("Should not update tagArray when initTags is called with empty tags option", function() {
            scope.initTags('{"tags_list": []}');
            expect(scope.tagsArray.length).toBe(0);
            expect(scope.tagsArray[0]).toBe(undefined);
        });

        it("Should not update tagArray items when initTags is called with tags option whose item key starts with aws:", function() {
            scope.initTags('{"tags_list": [{"name": "1", "value": "a", "propagate_at_launch": true},{"name": "aws:2", "value": "b"}, {"name": "3", "value": "c"}]}');
            expect(scope.tagsArray.length).toBe(2);
            expect(scope.tagsArray[0].name).toBe("1");
            expect(scope.tagsArray[0].value).toBe("a");
            expect(scope.tagsArray[1].name).toBe("3");
            expect(scope.tagsArray[1].value).toBe("c");
        });

        it("Should not update tagArray items when initTags is called with tags option whose item key starts with euca:", function() {
            scope.initTags('{"tags_list": [{"name": "euca:1", "value": "a", "propagate_at_launch": true},{"name": "2", "value": "b"}, {"name": "3", "value": "c"}]}');
            expect(scope.tagsArray.length).toBe(2);
            expect(scope.tagsArray[0].name).toBe("2");
            expect(scope.tagsArray[0].value).toBe("b");
            expect(scope.tagsArray[1].name).toBe("3");
            expect(scope.tagsArray[1].value).toBe("c");
        });

        it("Should initialize tagEditor when initTags is called", function() {
            scope.initTags('{"tags_list": []}');
            expect(scope.tagEditor.length).not.toBe(0);
        });

        it("Should initialize tagInputs when initTags is called", function() {
            scope.initTags('{"tags_list": []}');
            expect(scope.tagInputs.length).not.toBe(0);
        });

        it("Should initialize tagsTextarea when initTags is called", function() {
            scope.initTags('{"tags_list": []}');
            expect(scope.tagsTextarea.length).not.toBe(0);
        });
    });

    describe("Function removeTag Test", function() {

        beforeEach(function() {
            scope.initTags('{"tags_list": [{"name": "1", "value": "a", "propagate_at_launch": true},{"name": "2", "value": "b"}, {"name": "3", "value": "c"}]}');
        });

        it("Should remove tagArray item when removeTag is called with index", function() {
            expect(scope.tagsArray.length).toBe(3);
            expect(scope.tagsArray[2].name).toBe("3");
            expect(scope.tagsArray[2].value).toBe("c");
            scope.removeTag(1, {"preventDefault": function(){}});
            expect(scope.tagsArray.length).toBe(2);
            expect(scope.tagsArray[1].name).toBe("3");
            expect(scope.tagsArray[1].value).toBe("c");
        });

        it("Should emit tagUpdate when removeTag is called", function() {
            spyOn(scope, '$emit');
            scope.removeTag(1, {"preventDefault": function(){}});
            expect(scope.$emit).toHaveBeenCalledWith('tagUpdate');
        });
    });

    describe("Function addTag Test", function() {

        beforeEach(function() {
            scope.initTags('{"tags_list": [{"name": "1", "value": "a", "propagate_at_launch": true},{"name": "2", "value": "b"}, {"name": "3", "value": "c"}]}');
        });

        it("Should call checkRequiredInput when addTag is called", function() {
            spyOn(scope, 'checkRequiredInput');
            scope.addTag({"preventDefault": function(){}});
            expect(scope.checkRequiredInput).toHaveBeenCalled();
        });

        it("Should update tagArray when addTag is called and a new tag is added", function() {
            scope.newTagKey = "newKey";
            scope.newTagValue = "newValue";
            $('#autoscale-tag-name-input-div .key').val(scope.newTagKey);
            $('#autoscale-tag-value-input-div .value').val(scope.newTagValue);
            scope.addTag({"currentTarget": "#add-tag-btn", "preventDefault": function(){}});
            expect(scope.tagsArray.length).toBe(4);
            expect(scope.tagsArray[3].name).toBe("newKey");
            expect(scope.tagsArray[3].value).toBe("newValue");
            expect(scope.tagsArray[3].fresh).toBeTruthy();
        });

        it("Should emit tagUpdate when addTag is called and a new tag is added", function() {
            spyOn(scope, '$emit');
            scope.newTagKey = "newKey";
            scope.newTagValue = "newValue";
            $('#autoscale-tag-name-input-div .key').val(scope.newTagKey);
            $('#autoscale-tag-value-input-div .value').val(scope.newTagValue);
            scope.addTag({"currentTarget": "#add-tag-btn", "preventDefault": function(){}});
            expect(scope.$emit).toHaveBeenCalledWith('tagUpdate');
        });

        it("Should call syncTags when addTag is called and a new tag is added", function() {
            spyOn(scope, 'syncTags');
            scope.newTagKey = "newKey";
            scope.newTagValue = "newValue";
            $('#autoscale-tag-name-input-div .key').val(scope.newTagKey);
            $('#autoscale-tag-value-input-div .value').val(scope.newTagValue);
            scope.addTag({"currentTarget": "#add-tag-btn", "preventDefault": function(){}});
            expect(scope.syncTags).toHaveBeenCalled();
        });

        it("Should clear the new tag input fields when addTag is called and a new tag is added", function() {
            scope.newTagKey = "newKey";
            scope.newTagValue = "newValue";
            $('#autoscale-tag-name-input-div .key').val(scope.newTagKey);
            $('#autoscale-tag-value-input-div .value').val(scope.newTagValue);
            scope.addTag({"currentTarget": "#add-tag-btn", "preventDefault": function(){}});
            expect(scope.newTagKey).toBe('');
            expect(scope.newTagValue).toBe('');
            expect($('#autoscale-tag-name-input-div .key').val()).toBe("");
            expect($('#autoscale-tag-value-input-div .value').val()).toBe("");
        });

        it("Should not update tagsArray when addTag is called and a new tag key already exists", function() {
            scope.newTagKey = "3";
            scope.newTagValue = "newValue";
            $('#autoscale-tag-name-input-div .key').val(scope.newTagKey);
            $('#autoscale-tag-value-input-div .value').val(scope.newTagValue);
            scope.addTag({"currentTarget": "#add-tag-btn", "preventDefault": function(){}});
            expect(scope.tagsArray.length).toBe(3);
            expect(scope.tagsArray[3]).toBe(undefined);
        });
    });

    describe("Function getSafeTitle Test", function() {

        it("Should return a sanitized string consist of tag name + '=' + tag value when getSafeTitle is called", function() {
            var returnValue = scope.getSafeTitle({"name": "tagname&", "value": "tagvalue"});
            expect(returnValue).toBe("tagname&amp; = tagvalue");
        });
    });

    describe("Function togglePropagateCheckbox Test", function() {

        it("Should return false when the value of propagate-checkbox true and togglePropagateCheckbox is called", function() {
            var checkbox = $('#propagate-checkbox');
            checkbox.prop('checked', true);
            scope.togglePropagateCheckbox();
            var returnValue = checkbox.prop('checked');
            expect(returnValue).not.toBeTruthy();
        });

        it("Should return true when the value of propagate-checkbox false and togglePropagateCheckbox is called", function() {
            var checkbox = $('#propagate-checkbox');
            checkbox.prop('checked', false);
            scope.togglePropagateCheckbox();
            var returnValue = checkbox.prop('checked');
            expect(returnValue).toBeTruthy();
        });
    });

    describe("Function setWatch Test", function() {

        beforeEach(function() {
            scope.initTags('{"tags_list": [{"name": "1", "value": "a", "propagate_at_launch": true},{"name": "2", "value": "b"}, {"name": "3", "value": "c"}]}');
        });

        it("Should call checkRequiredInput() when newTagKey is updated", function() {
            spyOn(scope, 'checkRequiredInput');
            scope.setWatch(); 
            scope.newTagKey = "newKey";
            scope.$apply();
            expect(scope.checkRequiredInput).toHaveBeenCalled();
        });

        it("Should call checkRequiredInput() when newTagValue is updated", function() {
            spyOn(scope, 'checkRequiredInput');
            scope.setWatch(); 
            scope.newTagValue = "newValue";
            scope.$apply();
            expect(scope.checkRequiredInput).toHaveBeenCalled();
        });

        it("Should call updateTagCount() when tagsArray is updated", function() {
            spyOn(scope, 'updateTagCount');
            scope.setWatch(); 
            scope.tagsArray = [{name: '1', value: 'a'},
                               {name: '2', value: 'b'},
                               {name: '3', value: 'c'}];
            scope.$apply();
            expect(scope.updateTagCount).toHaveBeenCalled();
        });
    });
});
