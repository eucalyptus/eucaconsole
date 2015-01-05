/**
 * @fileOverview Jasmine Unittest for Instance Types JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("InstanceTypesPage", function() {

    beforeEach(angular.mock.module('InstanceTypesPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('InstanceTypesCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/instances/instance_types.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of chosenCreateOptionText is empty", function() {
            expect(scope.chosenCreateOptionText).toEqual('');
        });

        it("Initial value of chosenNoResultsText is empty", function() {
            expect(scope.chosenNoResultsText).toEqual('');
        });

        it("Initial value of itemsLoading is true", function() {
            expect(scope.itemsLoading).toBeTruthy();
        });

        it("Initial value of isNotChanged is true", function() {
            expect(scope.isNotChanged).toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should set jsonEndpoint when initController() is called", function() {
            scope.initController('a', 'b');
            expect(scope.jsonEndpoint).toEqual('a');
        });

        it("Should call setWatch() when initController() is called", function() {
            spyOn(scope, 'setWatch');
            scope.initController('a', 'b');
            expect(scope.setWatch).toHaveBeenCalled();
        });
    });
});
