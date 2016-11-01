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
    
        var instance_json = '{"results": [' +
            '{"id": "i-1111111", "status": "running", "availability_zone": "one", "vpc_name": ""},' +
            '{"id": "i-2222222", "status": "running", "availability_zone": "two", "vpc_name": ""}' +
            ']}';
        $httpBackend.when('POST', '/instances/json').respond(200, instance_json);
    }));

    var element, scope;
    beforeEach(inject(function ($templateCache) {
        var template = '<instance-selector instance-list="[]" availability-zones="[]"></instance-selector>'
        element = $compile(template)($rootScope);
        $rootScope.$digest();
        $httpBackend.flush();
        scope = element.isolateScope();
    }));

    describe('Instance Selector Zone Interaction', function () {

        it('should have none selected initially', function() {
            expect(scope.instanceList.length == 2).toBe(true);
            expect(scope.instanceList.reduce(function(sum, curr) {
                    return sum + (curr.selected?1:0);
                }, 0) == 0).toBe(true);
        });

        it('should have one instance in zone one', function() {
            scope.availabilityZones = ['one'];
            expect(scope.instanceList.reduce(function(sum, curr) {
                    return sum + (curr.selected?1:0);
                }, 0) == 1).toBe(true);
        });
    });
});
