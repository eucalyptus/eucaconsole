/**
 * @fileOverview Jasmine Unittest for Instance Volumes JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("InstanceVolumes", function() {

    beforeEach(angular.mock.module('InstanceVolumes'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('InstanceVolumesCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/instances/instance_volumes.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of availableVolumeCount is 0", function() {
            expect(scope.availableVolumeCount).toEqual(0);
        });

        it("Initial value of instanceId is empty", function() {
            expect(scope.instanceId).toEqual('');
        });

        it("Initial value of initialLoading is true", function() {
            expect(scope.initialLoading).toBeTruthy();
        });

        it("Initial value of isDialogHelpExpanded is false", function() {
            expect(scope.isDialogHelpExpanded).not.toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should set instanceId when initController() is called and instance_id JSON is set", function() {
            scope.initController('{"instance_id": "i-12345678"}');
            expect(scope.instanceId).toEqual('i-12345678');
        });

        it("Should call setWatch() when initController() is called", function() {
            spyOn(scope, 'setWatch');
            scope.initController('{}');
            expect(scope.setWatch).toHaveBeenCalled();
        });
    });
});
