/**
 * @fileOverview Jasmin Unittest for TagEditor directive
 * @requires Jasmine, AngularJS mock
 */

describe('TagEditorModule', function () {

    beforeEach(angular.mock.module('TagEditorModule'));

    var $compile, $rootScope, $templateCache;
    var template = '<div ng-form="tagForm"><input name="key" ng-model="newTagKey"required tag-name/><input name="value" ng-model="newTagValue"tag-value/></div>';
    var mockTags = [
        {
            name: 'tag1',
            value: 'value1',
            propagate_at_launch: true
        },
        {
            name: 'tag2',
            value: 'value2',
            propagate_at_launch: false
        }
    ];

    beforeEach(angular.mock.inject(function (_$compile_, _$rootScope_, _$templateCache_) {
        $compile = _$compile_;
        $rootScope = _$rootScope_;
        $templateCache = _$templateCache_;

        $templateCache.put('mock.template.html', template);
    }));

    var element, scope;
    beforeEach(function () {
        element = $compile(
            '<tag-editor ng-model="foo" template="mock.template.html">' +
            JSON.stringify(mockTags) +
            '</tag-editor>'
        )($rootScope);
        $rootScope.$digest();

        scope = element.isolateScope();
        scope.tagForm.$valid = true;
        spyOn(scope.tagForm.key, '$setPristine').and.callThrough();
        spyOn(scope.tagForm.key, '$setUntouched').and.callThrough();
        spyOn(scope.tagForm.value, '$setPristine').and.callThrough();
        spyOn(scope.tagForm.value, '$setUntouched').and.callThrough();
    });

    it('should transclude content into the tags member', function () {
        expect(scope.tags).toEqual(mockTags);
    });

    it('should default showNameTag to true', function () {
        expect(scope.showNameTag).toBe(true);
    });

    describe('#addTag', function () {

        beforeEach(function () {
            scope.addTag({
                name: 'tag3',
                value: 'value3',
                propagate_at_launch: false
            });
        });

        it('should add a tag when called', function () {
            expect(scope.tags.length).toEqual(3);
        });

        it('should reset the form', function () {
            expect(scope.tagForm.key.$setPristine).toHaveBeenCalled();
            expect(scope.tagForm.key.$setUntouched).toHaveBeenCalled();
            expect(scope.tagForm.value.$setPristine).toHaveBeenCalled();
            expect(scope.tagForm.value.$setUntouched).toHaveBeenCalled();
        });
    });

    describe('#removeTag', function () {

        it('should remove a tag when removeTag is called with an index', function () {
            scope.removeTag(1);
            expect(scope.tags.length).toEqual(1);
        });
    });
});
