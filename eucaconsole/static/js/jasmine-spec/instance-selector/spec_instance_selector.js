/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Jasmine Unittest for Tag Editor JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("InstanceSelector", function() {

    beforeEach(angular.mock.module('InstancesSelectorModule'));

    var $compile, $rootScope, $timeout, $httpBackend;

    beforeEach(angular.mock.inject(
        function (_$compile_, _$rootScope_, _$templateCache_, _$timeout_, _$httpBackend_) {
            $compile = _$compile_;
            $rootScope = _$rootScope_;
            $templateCache = _$templateCache_;
            $timeout = _$timeout_;
            $httpBackend = _$httpBackend_;
        }
    ));

    beforeEach(inject(function ($templateCache) {
        var template = window.__html__['templates/elbs/instance-selector.pt'];
        $templateCache.put('/_template/elbs/instance-selector', template);
        var template2 = window.__html__['static/js/thirdparty/magic-search/magic_search.html'];
        $templateCache.put('/static/js/thirdparty/magic-search/magic_search.html', template2);
    }));

    var element, scope;
    beforeEach(inject(function ($templateCache) {
        var template = '<instance-selector instance-list="[]"></instance-selector>'
        element = $compile(template)($rootScope);
        $rootScope.$digest();
        $httpBackend.flush();
        scope = element.isolateScope();
    }));

    describe('scope of directive reduced', function () {

        it('should do something');
    });
});
