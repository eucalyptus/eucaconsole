/**
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
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of transitionalStates[0] is pending", function() {
            expect(scope.transitionalStates[0]).toEqual('pending');
        });

        it("Initial value of transitionalStates[1] is stopping", function() {
            expect(scope.transitionalStates[1]).toEqual('stopping');
        });

        it("Initial value of transitionalStates[2] is shutting-down", function() {
            expect(scope.transitionalStates[2]).toEqual('shutting-down');
        });

        it("Initial value of instanceState is empty", function() {
            expect(scope.instanceState).toEqual('');
        });

        it("Initial value of isFileUserData is false", function() {
            expect(scope.isFileUserData).not.toBeTruthy();
        });

        it("Initial value of isNotChanged is true", function() {
            expect(scope.isNotChanged).toBeTruthy();
        });

        it("Initial value of isSubmitted is false", function() {
            expect(scope.isSubmitted).not.toBeTruthy();
        });

        it("Initial value of isUpdating is false", function() {
            expect(scope.isUpdating).not.toBeTruthy();
        });

        it("Initial value of isNotStopped is true", function() {
            expect(scope.isNotStopped).toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should call getInstanceState() when initController() is called", function() {
            spyOn(scope, 'getInstanceState');
            scope.initController('{}');
            expect(scope.getInstanceState).toHaveBeenCalled();
        });
    });
});
