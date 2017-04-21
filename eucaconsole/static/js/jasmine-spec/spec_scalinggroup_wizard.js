/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
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

        it("should set initial value of isNotValid to true", function() {
            expect(scope.isNotValid).toBe(true);
        });

        it("should set initial value of scalingGroupName to empty string", function() {
            expect(scope.scalingGroupName).toEqual('');
        });

        it("should set initial value of launchConfig to empty string", function() {
            expect(scope.launchConfig).toEqual('');
        });

        it("should set initial value of healthCheckType to 'EC2'", function() {
            expect(scope.healthCheckType).toEqual('EC2');
        });

        it("should set initial value of healthCheckPeriod to 120", function() {
            expect(scope.healthCheckPeriod).toEqual(120);
        });

        it("should set initial value of minSize to 1", function() {
            expect(scope.minSize).toEqual(1);
        });

        it("should set initial value of desiredCapacity to 1", function() {
            expect(scope.desiredCapacity).toEqual(1);
        });

        it("should set initial value of maxSize to 1", function() {
            expect(scope.maxSize).toEqual(1);
        });
    });

    describe("#checkRequiredInput", function() {

        it("should be invalid when scalingGroupName is empty", function() {
            scope.currentStepIndex = 1;
            scope.scalingGroupName = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
        });

        it("should be invalid when launchConfig is empty", function() {
            scope.currentStepIndex = 1;
            scope.launchConfig = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
        });

        it("should be invalid input when minSize is empty", function() {
            scope.currentStepIndex = 1;
            scope.minSize = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
        });

        it("should be invalid when desiredCapacity is empty", function() {
            scope.currentStepIndex = 1;
            scope.desiredCapacity = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
        });

        it("should be invalid when maxSize is empty", function() {
            scope.currentStepIndex = 1;
            scope.maxSize = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
        });

        it("should be invalid when healthCheckPeriod is empty", function() {
            scope.currentStepIndex = 2;
            scope.healthCheckPeriod = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
        });

        it("should be invalid when availZones is empty", function() {
            scope.currentStepIndex = 2;
            scope.availZones = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
        });
    });

    describe("#setInitialValues", function () {
        beforeEach(function () {
            spyOn(scope, 'cleanLaunchConfigOptions');
        });

        it("should call cleanLaunchConfigOptions when setInitialValues is called", function () {
            scope.setInitialValues();
            expect(scope.cleanLaunchConfigOptions).toHaveBeenCalled();
        });
    });

});
