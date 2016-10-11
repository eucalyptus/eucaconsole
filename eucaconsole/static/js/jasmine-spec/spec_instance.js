/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Jasmine Unittest for Instance JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("InstancePage", function() {

    beforeEach(angular.mock.module('InstancePage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('InstancePageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/instances/instance_view.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/<link/g, "<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("should set initial value of transitionalStates[0] to 'pending'", function() {
            expect(scope.transitionalStates[0]).toEqual('pending');
        });

        it("should set initial value of transitionalStates[1] to 'stopping'", function() {
            expect(scope.transitionalStates[1]).toEqual('stopping');
        });

        it("should set initial value of transitionalStates[2] to 'shutting-down'", function() {
            expect(scope.transitionalStates[2]).toEqual('shutting-down');
        });

        it("should set initial value of instanceState to empty string", function() {
            expect(scope.instanceState).toEqual('');
        });

        it("should set initial value of isFileUserData to false", function() {
            expect(scope.isFileUserData).toBe(false);
        });

        it("should set initial value of isNotChanged to true", function() {
            expect(scope.isNotChanged).toBe(true);
        });

        it("should set initial value of isSubmitted to false", function() {
            expect(scope.isSubmitted).toBe(false);
        });

        it("should set initial value of isUpdating to false", function() {
            expect(scope.isUpdating).toBe(false);
        });

        it("should set initial value of isNotStopped to true", function() {
            expect(scope.isNotStopped).toBe(true);
        });
    });

    describe("#initController", function() {

        it("should call getInstanceState() when initController() is called", function() {
            spyOn(scope, 'getInstanceState');
            scope.initController('{"instance_state_json_url": "", "instance_userdata_json_url": ""}');
            expect(scope.getInstanceState).toHaveBeenCalled();
        });
    });
});
