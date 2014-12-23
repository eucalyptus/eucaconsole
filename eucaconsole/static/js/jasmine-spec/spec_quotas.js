/**
 * @fileOverview Jasmine Unittest for Quotas JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("Quotas", function() {

    beforeEach(angular.mock.module('Quotas'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('QuotasCtrl', {
            $scope: scope
        });
    }));

    describe("Initial Values Test", function() {

        it("Initial value of ec2_expanded is false", function() {
            expect(scope.ec2_expanded).not.toBeTruthy();
        });

        it("Initial value of s3_expanded is false", function() {
            expect(scope.s3_expanded).not.toBeTruthy();
        });

        it("Initial value of autoscale_expanded is false", function() {
            expect(scope.autoscale_expanded).not.toBeTruthy();
        });

        it("Initial value of elb_expanded is false", function() {
            expect(scope.elb_expanded).not.toBeTruthy();
        });

        it("Initial value of iam_expanded is false", function() {
            expect(scope.iam_expanded).not.toBeTruthy();
        });
    });

    describe("Function toggleEC2Content() Test", function() {

        it("Value of ec2_expanded is toggled when toggleEC2Content() is called", function() {
            scope.ec2_expanded = true;
            scope.toggleEC2Content();
            expect(scope.ec2_expanded).not.toBeTruthy();
        });
    });
});
