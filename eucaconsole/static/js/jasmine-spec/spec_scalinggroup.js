/**
 * @fileOverview Jasmine Unittest for Scalinggroup JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("ScalingGroupPage", function() {

    beforeEach(angular.mock.module('ScalingGroupPage'));

    var scope, ctrl, timeout;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope, $timeout) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Handle $timeout() events in Angular module 
        timeout = $timeout;
        // Create the controller
        ctrl = $controller('ScalingGroupPageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/scalinggroups/scalinggroup_view.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/<link/g, "<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of minSize is 1", function() {
            expect(scope.minSize).toEqual(1);
        });

        it("Initial value of desiredCapacity is 1", function() {
            expect(scope.desiredCapacity).toEqual(1);
        });

        it("Initial value of maxSize is 1", function() {
            expect(scope.maxSize).toEqual(1);
        });

        it("Initial value of isNotChanged is true", function() {
            expect(scope.isNotChanged).toBeTruthy();
        });

        it("Initial value of isSubmitted is false", function() {
            expect(scope.isSubmitted).not.toBeTruthy();
        });

        it("Initial value of pendingModalID is empty", function() {
            expect(scope.pendingModalID).toEqual('');
        });
    });

    describe("Function initController() Test", function() {

        it("Should call setInitialValues() when initController() is called", function() {
            spyOn(scope, 'setInitialValues');
            scope.initController('{}');
            expect(scope.setInitialValues).toHaveBeenCalled();
        });

        it("Should set policiesCount when initController() is called and policiies_count JSON is passed", function() {
            scope.policiesCount = 0;
            scope.initController('{"policies_count": 3}');
            expect(scope.policiesCount).toEqual(3);
        });

        it("Should set terminationPoliciesOrder when initController() is called and termination_policies JSON is passed", function() {
            scope.policiesCount = 0;
            scope.initController('{"termination_policies": ["NewestInstance", "ClosestToNextInstanceHour"]}');
            expect(scope.terminationPoliciesOrder[1]).toEqual('ClosestToNextInstanceHour');
        });
    });

    describe("Function setInitialValues Test", function() {

        beforeEach(function() {
            setFixtures('<select id="termination_policies"><option></option></select>');
        });

        it("Should call rearrangeTerminationPoliciesOptions when setInitialValues is called", function() {
            spyOn(scope, 'rearrangeTerminationPoliciesOptions');
            scope.setInitialValues();
            expect(scope.rearrangeTerminationPoliciesOptions).toHaveBeenCalled();
        });
    });

    describe("Function rearrangeTerminationPoliciesOptions Test", function() {

        beforeEach(function() {
            setFixtures('<select id="termination_policies"><option value="option1">1</option><option value="option2">2</option><option value="option3">3</option></select>');
        });

        it("Should update the order of options when rearrangeTerminationPoliciesOptions is called", function() {
            var terminationPolicies = ['option2', 'option3', 'option1'];
            scope.rearrangeTerminationPoliciesOptions(terminationPolicies); 
            var options = $('#termination_policies').find('option');
            expect($(options[0]).val()).toEqual('option2');
            expect($(options[1]).val()).toEqual('option3');
            expect($(options[2]).val()).toEqual('option1');
        });
    });

    describe("Watch terminationPolicies Test", function() {

        beforeEach(function() {
            setFixtures('<select id="termination_policies"><option></option></select>');
        });

        it("Should call updateTerminationPoliciesOrder when terminationPoliciesUpdate is updated", function() {
            spyOn(scope, 'updateTerminationPoliciesOrder');
            scope.setWatch();
            scope.terminationPolicies = ['NewestInstance', 'ClosestToNextInstanceHour'];
            scope.$apply();
            timeout.flush();
            expect(scope.updateTerminationPoliciesOrder).toHaveBeenCalled();
        });

        it("Should call rearrangeTerminationPoliciesOptions when terminationPoliciesUpdate is updated", function() {
            spyOn(scope, 'rearrangeTerminationPoliciesOptions');
            scope.setWatch();
            scope.terminationPolicies = ['NewestInstance', 'ClosestToNextInstanceHour'];
            scope.$apply();
            timeout.flush();
            expect(scope.rearrangeTerminationPoliciesOptions).toHaveBeenCalled();
        });
    });
});
