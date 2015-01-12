/**
 * @fileOverview Jasmine Unittest for Launchconfig Wizard JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("LaunchConfigWizard", function() {

    beforeEach(angular.mock.module('LaunchConfigWizard'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('LaunchConfigWizardCtrl', {
            $scope: scope
        });
    }));

    describe("Initial Values Test", function() {

        it("Initial value of isLoadingKeyPair is false", function() {
            expect(scope.isLoadingKeyPair).not.toBeTruthy();
        });

        it("Initial value of isLoadingSecurityGroup is false", function() {
            expect(scope.isLoadingSecurityGroup).not.toBeTruthy();
        });

        it("Initial value of isNotValid is true", function() {
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Initial value of launchconfigName is empty", function() {
            expect(scope.launchconfigName).toEqual('');
        });

        it("Initial value of keyPair is empty", function() {
            expect(scope.keyPair).toEqual('');
        });
    });

    describe("Function checkRequiredInput() Test", function() {

        it("Should invalid input when isNotValid is false and imageID is less 12 chars", function() {
            scope.isNotValid = false;
            scope.currentStepIndex = 1;
            scope.imageID = "emi-1234"; 
            scope.imageIDErrorClass = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
            expect(scope.imageIDErrorClass).toEqual('error');
        });

        it("Should invalid input when imageID is empty, but do not set the imageIDErrorClass", function() {
            scope.isNotValid = true;
            scope.currentStepIndex = 1;
            scope.imageID = ''; 
            scope.imageIDErrorClass = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
            expect(scope.imageIDErrorClass).toEqual('');
        });

        it("Should invalid input when imageID is more 12 chars", function() {
            scope.currentStepIndex = 1;
            scope.imageID = "emi-1234567890" 
            scope.imageIDErrorClass = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
            expect(scope.imageIDErrorClass).toEqual('error');
        });

        it("Should invalid input when imageID is doesn't start with 'emi-'", function() {
            scope.currentStepIndex = 1;
            scope.imageID = "1234567890ab"; 
            scope.imageIDErrorClass = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
            expect(scope.imageIDErrorClass).toEqual('error');
        });

        it("Should valid input when imageID is 12 chars and begins with 'emi-'", function() {
            scope.currentStepIndex = 1;
            scope.imageID = "emi-12345678"; 
            scope.imageIDErrorClass = 'error';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).not.toBeTruthy();
            expect(scope.imageIDErrorClass).toEqual('');
        });

        it("Should invalid input when launchconfigName is empty", function() {
            scope.currentStepIndex = 2;
            scope.launchconfigName = ''; 
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when keyPair is empty", function() {
            scope.currentStepIndex = 3;
            scope.keyPair = ''; 
            scope.urlParams = {};
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when securityGroups is empty", function() {
            scope.currentStepIndex = 3;
            scope.securityGroups = []; 
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });
    });
});
