/**
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
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of policyJsonEndpoint is empty", function() {
            expect(scope.policyJsonEndpoint).toEqual('');
        });

        it("Initial value of policyAPIVersion is 2012-10-17", function() {
            expect(scope.policyAPIVersion).toEqual('2012-10-17');
        });

        it("Initial value of cloudType is euca", function() {
            expect(scope.cloudType).toEqual('euca');
        });

        it("Initial value of lastSelectedTabKey is policyWizard-selectedTab", function() {
            expect(scope.lastSelectedTabKey).toEqual('policyWizard-selectedTab');
        });

        it("Initial value of languageCode is en", function() {
            expect(scope.languageCode).toEqual('en');
        });

        it("Initial value of confirmed is false", function() {
            expect(scope.confirmed).not.toBeTruthy();
        });

        it("Initial value of isCreating is false", function() {
            expect(scope.isCreating).not.toBeTruthy();
        });

        it("Initial value of nameConflictKey is doNotShowPolicyNameConflictWarning", function() {
            expect(scope.nameConflictKey).toEqual('doNotShowPolicyNameConflictWarning');
        });
    });

    describe("Function initController() Test", function() {

        it("Should set cloudType when initController() is called and cloudType JSON is set", function() {
            scope.initController('{"cloudType": "aws", "policyActions": [{"actions": []}]}');
            expect(scope.cloudType).toEqual('aws');
        });

        it("Should call initDateTimePickers() when initController() is called and cloudType is euca", function() {
            spyOn(scope, 'initDateTimePickers');
            scope.initController('{"cloudType": "euca", "policyActions": [{"actions": []}]}');
            expect(scope.initDateTimePickers).toHaveBeenCalled();
        });
    });
});
