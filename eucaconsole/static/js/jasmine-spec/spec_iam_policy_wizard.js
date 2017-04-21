/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview Jasmine Unittest for IAM Policy Wizard JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("IAMPolicyWizard", function() {

    beforeEach(angular.mock.module('IAMPolicyWizard'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('IAMPolicyWizardCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/policies/iam_policy_wizard.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/<link/g, "<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("should set initial value of policyJsonEndpoint to empty string", function() {
            expect(scope.policyJsonEndpoint).toEqual('');
        });

        it("should set initial value of policyAPIVersion to '2012-10-17'", function() {
            expect(scope.policyAPIVersion).toEqual('2012-10-17');
        });

        it("should set initial value of cloudType to 'euca'", function() {
            expect(scope.cloudType).toEqual('euca');
        });

        it("should set initial value of lastSelectedTabKey to 'policyWizard-selectedTab'", function() {
            expect(scope.lastSelectedTabKey).toEqual('policyWizard-selectedTab');
        });

        it("should set initial value of languageCode to 'en'", function() {
            expect(scope.languageCode).toEqual('en');
        });

        it("should set initial value of confirmed to false", function() {
            expect(scope.confirmed).toBe(false);
        });

        it("should set initial value of isCreating to false", function() {
            expect(scope.isCreating).toBe(false);
        });

        it("should set initial value of nameConflictKey to 'doNotShowPolicyNameConflictWarning'", function() {
            expect(scope.nameConflictKey).toEqual('doNotShowPolicyNameConflictWarning');
        });
    });

    describe("#initController", function() {

        beforeEach(function () {
            spyOn(scope, 'initActionContainers');
            spyOn(scope, 'initSelectedTab');
            spyOn(scope, 'initChoices');
            spyOn(scope, 'setupListeners');
        });

        it("should set cloudType when initController() is called and cloudType JSON is set", function() {
            scope.initController('{"cloudType": "aws", "policyActions": [{"actions": []}]}');
            expect(scope.cloudType).toEqual('aws');
        });

        it("should call initActionContainers when initController is called", function () {
            scope.initController('{"cloudType": "euca", "policyActions": [{"actions": []}]}');
            expect(scope.initActionContainers).toHaveBeenCalled();
        });

        it("should call initSelectedTab when initController is called", function () {
            scope.initController('{"cloudType": "euca", "policyActions": [{"actions": []}]}');
            expect(scope.initSelectedTab).toHaveBeenCalled();
        });

        it("should call initChoices when initController is called", function () {
            scope.initController('{"cloudType": "euca", "policyActions": [{"actions": []}]}');
            expect(scope.initChoices).toHaveBeenCalled();
        });

        it("should call setupListeners when initController is called", function () {
            scope.initController('{"cloudType": "euca", "policyActions": [{"actions": []}]}');
            expect(scope.setupListeners).toHaveBeenCalled();
        });
    });
});
