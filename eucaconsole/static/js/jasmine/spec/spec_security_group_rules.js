/**
 * @fileOverview Jasmine Unittest for SecurityGroupRules JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("SecurityGroupRules", function() {

    beforeEach(angular.mock.module('SecurityGroupRules'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('SecurityGroupRulesCtrl', {
            $scope: scope
        });
    }));

    describe("Initial Values Test", function() {

        it("Initial value of isRuleNotComplete is true", function() {
            expect(scope.isRuleNotComplete).toBeTruthy();
        });

        it("Initial value of inboundButtonClass is 'active'", function() {
            expect(scope.inboundButtonClass).toEqual('active');
        });

        it("Initial value of outboundButtonClass is not 'active'", function() {
            expect(scope.outboundButtonClass).not.toEqual('active');
        });

        it("Initial value of ruleType is 'inbound'", function() {
            expect(scope.ruleType).toEqual('inbound');
        });
    });

    describe("Function addRuleButtonClass() Test", function() {

        it("Should disable the addRule button when the rule edit is in progress", function() {
            scope.isRuleNotComplete = true;
            scope.setAddRuleButtonClass(); 
            expect(scope.addRuleButtonClass).toEqual('disabled');
        });

        it("Should disable the addRule button when there exist duplicated rules", function() {
            scope.hasDuplicatedRule = true;
            scope.setAddRuleButtonClass(); 
            expect(scope.addRuleButtonClass).toEqual('disabled');
        });

        it("Should disable the addRule button  when the customProtocol contains error", function() {
            scope.customProtocolDivClass = 'error';
            scope.setAddRuleButtonClass(); 
            expect(scope.addRuleButtonClass).toEqual('disabled');
        });

        it("Should enable the addRule button when all conditions are met", function() {
            scope.isRuleNotComplete = false;
            scope.hasDuplicatedRule == false; 
            scope.customProtocolDivClass = '';
            scope.setAddRuleButtonClass(); 
            expect(scope.addRuleButtonClass).toEqual('');
        });
    });

    describe("Function clearRules() Test", function() {

        it("Should re-use resetValue() when clearing rules", function() {
            spyOn(scope, 'resetValues');
            scope.clearRules();
            expect(scope.resetValues).toHaveBeenCalled();
        });

        it("Should empty rules arrays and re-use syncRules() when clearing rules", function() {
            spyOn(scope, 'syncRules');
            scope.rulesArray = [1,2,3];
            scope.rulesEgressArray = [1,2,3];
            scope.clearRules();
            expect(scope.rulesArray).toBeEmptyArray();
            expect(scope.rulesEgressArray).toBeEmptyArray();
            expect(scope.syncRules).toHaveBeenCalled();
        });
    });
});
