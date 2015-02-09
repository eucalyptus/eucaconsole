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

        it("Initial value of rulesEditor is undefined", function() {
            expect(scope.rulesEditor).toEqual(undefined);
        });

        it("Initial value of rulesTextarea is undefined", function() {
            expect(scope.rulesTextarea).toEqual(undefined);
        });

        it("Initial value of rulesEgressTextarea is undefined", function() {
            expect(scope.rulesEgressTextarea).toEqual(undefined);
        });

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

        it("Initial value of securityGroupVPC is 'None'", function() {
            expect(scope.securityGroupVPC).toEqual('None');
        });
    });

    describe("Function initRules() Test", function() {

        it("Should set rulesArray when initRules is called ", function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
            expect(scope.rulesArray).toEqual([{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}]);
        });

        it("Should set rulesEgressArray when initRules is called ", function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
            expect(scope.rulesEgressArray).toEqual([{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}]);
        });

        it("Should set jsonEndpoint when initRules is called ", function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
            expect(scope.jsonEndpoint).toEqual("localhost/json");
        });

        it("Should set internetProtocolsJsonEndpoint when initRules is called ", function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
            expect(scope.internetProtocolsJsonEndpoint).toEqual("localhost/api");
        });

        it("Should initialize rulesEditor when initRules is called ", function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
            expect(scope.rulesEditor.length).not.toEqual(0);
        });

        it("Should initialize rulesTextarea when initRules is called ", function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
            expect(scope.rulesTextarea.length).not.toEqual(0);
        });

        it("Should initialize rulesEgressTextarea when initRules is called ", function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
            expect(scope.rulesEgressTextarea.length).not.toEqual(0);
        });

        it("Should call initInternetProtocols when initRules is called", function() {
            spyOn(scope, 'initInternetProtocols');
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
            expect(scope.initInternetProtocols).toHaveBeenCalled();
        });

        it("Should call syncRules when initRules is called", function() {
            spyOn(scope, 'syncRules');
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
            expect(scope.syncRules).toHaveBeenCalled();
        });

        it("Should call setWatchers when initRules is called", function() {
            spyOn(scope, 'setWatchers');
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
            expect(scope.setWatchers).toHaveBeenCalled();
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

        beforeEach(function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
        });

        it("Should clear rulesArrays when clearRules is called", function() {
            scope.clearRules();
            expect(scope.rulesArray).toBeEmptyArray();
        });

        it("Should clear rulesEgressArrays when clearRules is called", function() {
            scope.clearRules();
            expect(scope.rulesEgressArray).toBeEmptyArray();
        });

        it("Should call syncRules when clearRules is called", function() {
            spyOn(scope, 'syncRules');
            scope.clearRules();
            expect(scope.syncRules).toHaveBeenCalled();
        });

        it("Should use resetValue() when clearRules is called", function() {
            spyOn(scope, 'resetValues');
            scope.clearRules();
            expect(scope.resetValues).toHaveBeenCalled();
        });
    });

    describe("Function resetValues() Test", function() {

        it("Should set trafficType to 'ip' when resetValue is called", function() {
            scope.trafficType = '';
            scope.resetValues();
            expect(scope.trafficType).toEqual('ip');
        });

        it("Should set fromPort to '' when resetValue is called", function() {
            scope.fromPort = '8888';
            scope.resetValues();
            expect(scope.fromPort).toEqual('');
        });

        it("Should set toPort to '' when resetValue is called", function() {
            scope.toPort = '8888';
            scope.resetValues();
            expect(scope.toPort).toEqual('');
        });

        it("Should set cidrIp to '' when resetValue is called", function() {
            scope.cidrIp = '1.1.1.1/0';
            scope.resetValues();
            expect(scope.cidrIp).toEqual('');
        });

        it("Should set selectedProtocol to '' when resetValue is called", function() {
            scope.selectedProtocol = 'SSH';
            scope.resetValues();
            expect(scope.selectedProtocol).toEqual('');
        });

        it("Should set customProtocol to '' when resetValue is called", function() {
            scope.customProtocol = 'SSH';
            scope.resetValues();
            expect(scope.customProtocol).toEqual('');
        });

        it("Should set icmpRange to '-1' when resetValue is called", function() {
            scope.icmpRange = '100';
            scope.resetValues();
            expect(scope.icmpRange).toEqual('-1');
        });

        it("Should set groupName to '' when resetValue is called", function() {
            scope.groupName = 'groupname';
            scope.resetValues();
            expect(scope.groupName).toEqual('');
        });

        it("Should set ipProtocol to '' when resetValue is called", function() {
            scope.ipProtocol = 'udp';
            scope.resetValues();
            expect(scope.ipProtocol).toEqual('tcp');
        });

        it("Should set hasDuplicatedRule to false when resetValue is called", function() {
            scope.hasDuplicatedRule = true;
            scope.resetValues();
            expect(scope.hasDuplicatedRule).not.toBeTruthy();
        });

        it("Should set hasInvalidOwner to false when resetValue is called", function() {
            scope.hasInvalidOwner = true;
            scope.resetValues();
            expect(scope.hasInvalidOwner).not.toBeTruthy();
        });

        it("Should set #ip-protocol-select's 'selectedIndex' value to -1 after resetting values", function() {
            scope.resetValues();
            expect($('#ip-protocol-select').prop('selectedIndex')).toEqual(-1);
        });

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
    });

    describe("Function syncRules() Test", function() {

        beforeEach(function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
        });

        it("Should set rulesTextarea  when syncRules is called", function() {
            scope.syncRules();
            expect(scope.rulesTextarea.val()).toBe('[{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}]');
        });

        it("Should set rulesEgressTextarea  when syncRules is called", function() {
            scope.syncRules();
            expect(scope.rulesEgressTextarea.val()).toBe('[{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}]');
        });

        it("Should call resetValues() when syncRules is called", function() {
            spyOn(scope, 'resetValues');
            scope.syncRules();
            expect(scope.resetValues).toHaveBeenCalled();
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

    describe("Watch securityGroupVPC Test", function() {

        it("Should call getAllSecurityGroupVPC when securityGroupVPC is updated", function() {
            spyOn(scope, 'getAllSecurityGroups');
            scope.setWatchers();
            scope.securityGroupVPC = "vpc-12345678";
            scope.$apply();
            expect(scope.getAllSecurityGroups).toHaveBeenCalledWith('vpc-12345678');
        });
    });

    describe("Function initModal Test", function() {

        it("Should call getAllSecurityGroupVPC when initModal is called", function() {
            spyOn(scope, 'getAllSecurityGroups');
            scope.setWatchers();
            scope.securityGroupVPC = "vpc-12345678";
            scope.$broadcast('initModal');
            expect(scope.getAllSecurityGroups).toHaveBeenCalledWith('vpc-12345678');
        });
    });

    describe("Function updateVPC Test", function() {

        beforeEach(function() {
            setFixtures('<select id="securitygroup_vpc_network"></select>');
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
        });

        it("Should update securityGroupVPC when updateVPC is called", function() {
            scope.setWatchers();
            scope.$broadcast('updateVPC', 'vpc-12345678');
            expect(scope.securityGroupVPC).toEqual('vpc-12345678');
        });

        it("Shouldn't update securityGroupVPC when updateVPC is called and vpc value is undefined", function() {
            scope.setWatchers();
            scope.$broadcast('updateVPC', undefined);
            expect(scope.securityGroupVPC).toEqual('None');
        });

        it("Should return immediately when updateVPC is called and vpc value is not changed", function() {
            spyOn(scope, 'adjustIPProtocolOptions');
            scope.securityGroupVPC = 'vpc-12345678';
            scope.setWatchers();
            scope.$broadcast('updateVPC', 'vpc-12345678');
            expect(scope.adjustIPProtocolOptions).not.toHaveBeenCalled();
        });

        it("Should call selectRuleType when updateVPC is called and vpc value is 'None'", function() {
            spyOn(scope, 'selectRuleType');
            scope.securityGroupVPC = 'vpc-12345678';
            scope.setWatchers();
            scope.$broadcast('updateVPC', 'None');
            expect(scope.selectRuleType).toHaveBeenCalled();
        });

        it("Should call clearRules when updateVPC is called", function() {
            spyOn(scope, 'clearRules');
            scope.setWatchers();
            scope.$broadcast('updateVPC', 'vpc-12345678');
            expect(scope.clearRules).toHaveBeenCalled();
        });

        it("Should call addDefaultOutboundRule when updateVPC is called and vpc is not 'None'", function() {
            spyOn(scope, 'addDefaultOutboundRule');
            scope.setWatchers();
            scope.$broadcast('updateVPC', 'vpc-12345678');
            expect(scope.addDefaultOutboundRule).toHaveBeenCalled();
        });

        it("Shouldn't call addDefaultOutboundRule when updateVPC is called and vpc is 'None'", function() {
            spyOn(scope, 'addDefaultOutboundRule');
            scope.securityGroupVPC = 'vpc-12345678';
            scope.setWatchers();
            scope.$broadcast('updateVPC', 'None');
            expect(scope.addDefaultOutboundRule).not.toHaveBeenCalled();
        });
    });

});
