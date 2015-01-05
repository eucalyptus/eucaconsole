/**
 * @fileOverview Jasmine Unittest for SecurityGroup JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("SecurityGroupPage", function() {

    beforeEach(angular.mock.module('SecurityGroupPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('SecurityGroupPageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/securitygroups/securitygroup_view.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of isNotValid is true", function() {
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Initial value of isNotChanged is true", function() {
            expect(scope.isNotChanged).toBeTruthy();
        });

        it("Initial value of isSubmitted is false", function() {
            expect(scope.isSubmitted).not.toBeTruthy();
        });

        it("Initial value of securityGroupName is undefined", function() {
            expect(scope.securityGroupName).toEqual(undefined);
        });

        it("Initial value of securityGroupDescription is undefined", function() {
            expect(scope.securityGroupDescription).toEqual(undefined);
        });

        it("Initial value of securityGroupVPC is undefined", function() {
            expect(scope.securityGroupVPC).toEqual(undefined);
        });
    });

    describe("Function initController() Test", function() {

        it("Should set securityGroupVPC when initController() is called and default_vpc_network JSON is set", function() {
            scope.initController('{"default_vpc_network": "vpc-12345678"}');
            expect(scope.securityGroupVPC).toEqual('vpc-12345678');
        });

        it("Should call setWatch() when initController() is called", function() {
            spyOn(scope, 'setWatch');
            scope.initController('{"default_vpc_network": "vpc-12345678"}');
            expect(scope.setWatch).toHaveBeenCalled();
        });
    });
});
