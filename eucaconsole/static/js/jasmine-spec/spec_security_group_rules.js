/**
 * @fileOverview Jasmine Unittest for SecurityGroupRules JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("SecurityGroupRules", function() {

    beforeEach(angular.mock.module('SecurityGroupRules'));

    var scope, httpBackend, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($rootScope, $httpBackend, $controller) {
        httpBackend = $httpBackend;
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('SecurityGroupRulesCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        //jasmine.getFixtures().fixturesPath = "/templates/panels";
        //loadFixtures("securitygroup_rules.pt");
        var template = window.__html__['templates/panels/securitygroup_rules.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

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

    describe("Function resetValues() Test", function() {


        it("Should call cleanupSelections() after resetting values", function() {
            spyOn(scope, 'cleanupSelections');
            scope.resetValues();
            expect(scope.cleanupSelections).toHaveBeenCalled();
        });

        it("Should call adjustIPProtocolOptions() after resetting values", function() {
            spyOn(scope, 'adjustIPProtocolOptions');
            scope.resetValues();
            expect(scope.adjustIPProtocolOptions).toHaveBeenCalled();
        });

        it("Should set #ip-protocol-select's 'selectedIndex' value to -1 after resetting values", function() {
            scope.resetValues();
            expect($('#ip-protocol-select').prop('selectedIndex')).toEqual(-1);
        });
    });

    describe("Template Label Test", function() {

        it("Should #inbound-rules-tab link be labeled 'Inbound'", function() {
            expect($('#inbound-rules-tab').text()).toEqual('Inbound');
        });

        it("Should #outbound-rules-tab link be labeled 'Outbound'", function() {
            expect($('#outbound-rules-tab').text()).toEqual('Outbound');
        });
    });

    describe("Function initInternetProtocol() Test", function() {

        beforeEach(function() {
            setFixtures('<input id="csrf_token" name="csrf_token" type="hidden" value="2a06f17d6872143ed806a695caa5e5701a127ade">');
            scope.internetProtocolsJsonEndpoint  = "internet_protocols_json";
            httpBackend.expect('POST', scope.internetProtocolsJsonEndpoint, 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade')
                .respond(200, {
                    "success": true,
                    "results": angular.toJson({"internet_protocols": [[0, "HOPOPT"], [1, "ICMP"], [2, "IGMP"]]}) 
                });
        });

        afterEach(function() {
            httpBackend.verifyNoOutstandingExpectation();
            httpBackend.verifyNoOutstandingRequest();
        });

        it("Should have internetProtocols[] initialized after initInternetProtocols() is successful", function() {
            scope.initInternetProtocols();
            httpBackend.flush();
            expect(scope.internetProtocols[0]).toEqual('HOPOPT');
            expect(scope.internetProtocols[1]).toEqual('ICMP');
            expect(scope.internetProtocols[2]).toEqual('IGMP');
        });

        it("Should call scanForCustomProtocol() after initInternetProtocols() is successful", function() {
            spyOn(scope, 'scanForCustomProtocols');
            scope.initInternetProtocols();
            httpBackend.flush();
            expect(scope.scanForCustomProtocols).toHaveBeenCalled();
        });
    });

    describe("Function getAllSecurityGroups() Test", function() {

        var vpc = 'vpc-12345678';

        beforeEach(function() {
            setFixtures('<input id="csrf_token" name="csrf_token" type="hidden" value="2a06f17d6872143ed806a695caa5e5701a127ade">');
            scope.jsonEndpoint  = "securitygroup_json";
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + vpc
            httpBackend.expect('POST', scope.jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
        });

        afterEach(function() {
            httpBackend.verifyNoOutstandingExpectation();
            httpBackend.verifyNoOutstandingRequest();
        });

        it("Should have securityGroupList[] initialized after getAllSecurityGroups() is successful", function() {
            scope.getAllSecurityGroups(vpc);
            httpBackend.flush();
            expect(scope.securityGroupList[0]).toEqual('SSH');
            expect(scope.securityGroupList[1]).toEqual('HTTP');
            expect(scope.securityGroupList[2]).toEqual('HTTPS');
        });
    });

    describe("Function createRuleArrayBlock() Test", function() {

        it("Should call getGroupIdByName() if trafficType is 'securitygroup' and has groupName", function() {
            spyOn(scope, 'getGroupIdByName');
            scope.groupName = "12345678/my group";
            scope.trafficType = 'securitygroup';
            scope.createRuleArrayBlock();
            expect(scope.getGroupIdByName).toHaveBeenCalled();
        });

        it("Should call adjustIpProtocol() when createRuleArrayBlock() is called", function() {
            spyOn(scope, 'adjustIpProtocol');
            scope.createRuleArrayBlock();
            expect(scope.adjustIpProtocol).toHaveBeenCalled();
        });

        it("Should match the output values when createRuleArrayBlock() is returned", function() {
            scope.fromPort = 22;
            scope.toPort = 22;
            scope.ipProtocol = 'tcp';
            scope.trafficType = 'ip';
            scope.cidrIp = '0.0.0.0/0'; 
            scope.ruleType = 'inbound';
            var output = scope.createRuleArrayBlock();
            expect(output).toEqual({
                'from_port': 22,
                'to_port': 22,
                'ip_protocol': 'tcp',
                'custom_protocol': undefined,
                'grants': [{
                    'cidr_ip': '0.0.0.0/0',
                    'group_id': null,
                    'name': null,
                    'owner_id': null 
                }],
                'rule_type': 'inbound',
                'fresh': 'new'
            });
        });
    });
});
