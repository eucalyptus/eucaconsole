/**
 * @fileOverview Jasmine Unittest for KeypairPage JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("KeypairPage", function() {

    beforeEach(angular.mock.module('KeypairPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('KeypairPageCtrl', {
            $scope: scope
        });
    }));

    describe("Initial Values Test", function() {

        it("Initial value of isNotValid is true", function() {
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Initial value of keypairName is empty", function() {
            expect(scope.keypairName).toEqual('');
        });

        it("Initial value of keypairMaterial is empty", function() {
            expect(scope.keypairMaterial).toEqual('');
        });

        it("Initial value of routeID is empty", function() {
            expect(scope.routeID).toEqual('');
        });
    });

    describe("Function checkRequiredInput() Test", function() {

        it("Should invalid input when keypairName is empty", function() {
            scope.keypairName = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when keypairName is undefined", function() {
            scope.keypairName = undefined;
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when routeID is 'new2' and keypairMaterial is empty", function() {
            scope.routeID = 'new2';
            scope.keypairMaterial = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when routeID is 'new2' and keypairMaterial is undefined", function() {
            scope.routeID = 'new2';
            scope.keypairMaterial = undefined;
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should ignore keypairMaterial value when routeID is not 'new2'", function() {
            scope.routeID = '';
            scope.keypairName = 'my keypair';
            scope.keypairMaterial = '';
            scope.isNotValid = true;
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).not.toBeTruthy();
        });

        it("Should validate input when all conditions are met", function() {
            scope.routeID = '';
            scope.keypairName = 'my keypair';
            scope.isNotValid = true;
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).not.toBeTruthy();
        });

        it("Should validate input when routeID is 'new2' and all conditions are met", function() {
            scope.routeID = 'new2';
            scope.keypairName = 'my keypair';
            scope.keypairMaterial = 'my keypair material';
            scope.isNotValid = true;
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).not.toBeTruthy();
        });
    });
});
