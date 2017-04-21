/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview Jasmine Unittest for Instances JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("InstancesPage", function() {

    beforeEach(angular.mock.module('InstancesPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('InstancesCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/instances/instances.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/<link/g, "<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("should set initial value of instanceID to empty string", function() {
            expect(scope.instanceID).toEqual('');
        });

        it("should set initial value of fileName to empty string", function() {
            expect(scope.fileName).toEqual('');
        });

        it("should set initial value of ipAddressList to empty array", function() {
            expect(scope.ipAddressList).toEqual([]);
        });
    });

    describe("#initController", function() {

        it("should call initChosenSelectors() when initController() is called", function() {
            spyOn(scope, 'initChosenSelectors');
            scope.initController('{"addresses_json_items_endpoint": ""}');
            expect(scope.initChosenSelectors).toHaveBeenCalled();
        });
    });
});
