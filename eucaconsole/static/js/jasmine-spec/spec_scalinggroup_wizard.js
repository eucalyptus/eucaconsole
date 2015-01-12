/**
 * @fileOverview Jasmine Unittest for Scalinggroup Wizard JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("ScalingGroupWizard", function() {

    beforeEach(angular.mock.module('ScalingGroupWizard'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('ScalingGroupWizardCtrl', {
            $scope: scope
        });
    }));

    describe("Initial Values Test", function() {

        it("Initial value of isNotValid is true", function() {
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Initial value of scalingGroupName is empty", function() {
            expect(scope.scalingGroupName).toEqual('');
        });

        it("Initial value of launchConfig is empty", function() {
            expect(scope.launchConfig).toEqual('');
        });

        it("Initial value of healthCheckType is EC2", function() {
            expect(scope.healthCheckType).toEqual('EC2');
        });

        it("Initial value of healthCheckPeriod is 120", function() {
            expect(scope.healthCheckPeriod).toEqual(120);
        });

        it("Initial value of minSize is 1", function() {
            expect(scope.minSize).toEqual(1);
        });

        it("Initial value of desiredCapacity is 1", function() {
            expect(scope.desiredCapacity).toEqual(1);
        });

        it("Initial value of maxSize is 1", function() {
            expect(scope.maxSize).toEqual(1);
        });
    });

    describe("Function checkRequiredInput() Test", function() {

        it("Should invalid input when scalingGroupName is empty", function() {
            scope.currentStepIndex = 1;
            scope.scalingGroupName = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when launchConfig is empty", function() {
            scope.currentStepIndex = 1;
            scope.launchConfig = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when minSize is empty", function() {
            scope.currentStepIndex = 1;
            scope.minSize = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when desiredCapacity is empty", function() {
            scope.currentStepIndex = 1;
            scope.desiredCapacity = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when maxSize is empty", function() {
            scope.currentStepIndex = 1;
            scope.maxSize = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when healthCheckPeriod is empty", function() {
            scope.currentStepIndex = 2;
            scope.healthCheckPeriod = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when availZones is empty", function() {
            scope.currentStepIndex = 2;
            scope.availZones = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });
    });
});
