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
    beforeEach(angular.mock.inject(function($controller, $rootScope, $timeout, $httpBackend) {
        httpBackend = $httpBackend;
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        scope.timeout = $timeout;
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
        template = template.replace(/<link/g, "<ignore_link"); 
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

    describe("Function cleanupSelections() Test", function() {

        it("Should remove the first option from ip-protocol-select element if the option is empty", function() {
            setFixtures('<select id="ip-protocol-select"><option></option><option value="1">1</option></select>');
            expect($('#ip-protocol-select').children('option').first().html()).toEqual('');
            scope.cleanupSelections();
            scope.timeout.flush();
            expect($('#ip-protocol-select').children('option').first().html()).not.toEqual('');
        });  

        it("Should remove the first option from groupname-select element if the option is empty", function() {
            setFixtures('<select id="groupname-select"><option></option><option value="1">1</option></select>');
            expect($('#groupname-select').children('option').first().html()).toEqual('');
            scope.cleanupSelections();
            scope.timeout.flush();
            expect($('#groupname-select').children('option').first().html()).not.toEqual('');
        });  
    });

    describe("Function checkRequiredInput() Test", function() {

        it("Should set isRuleNotComplete to true if hasDuplicatedRule is true when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = true;
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).toBeTruthy();
        }); 

        it("Should set isRuleNotComplete to true if selectedProtocol is 'custom' and customProtocol empty when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = 'custom';
            scope.customProtocol = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).toBeTruthy();
        }); 

        it("Should set isRuleNotComplete to true if selectedProtocol is 'custom' and customProtocolDivClass contains 'error' when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = 'custom';
            scope.customProtocolDivClass = 'error';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).toBeTruthy();
        }); 

        it("Should set isRuleNotComplete to true if selectedProtocol is not ['custom', 'icmp', '-1'] and fromPort is empty when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = 'tcp';
            scope.fromPort = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).toBeTruthy();
        }); 

        it("Should set isRuleNotComplete to true if selectedProtocol is not ['custom', 'icmp', '-1'] and fromPort is undefined when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = 'tcp';
            scope.fromPort = undefined;
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).toBeTruthy();
        }); 

        it("Should set isRuleNotComplete to true if selectedProtocol is not ['custom', 'icmp', '-1'] and toPort is empty when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = 'tcp';
            scope.fromPort = '22';
            scope.toPort = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).toBeTruthy();
        }); 

        it("Should set isRuleNotComplete to true if selectedProtocol is not ['custom', 'icmp', '-1'] and toPort is undefined when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = 'tcp';
            scope.fromPort = '22';
            scope.toPort = undefined;
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).toBeTruthy();
        }); 

        it("Should not set isRuleNotComplete to true if selectedProtocol is 'icmp' and fromPort is empty when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = 'icmp';
            scope.fromPort = '';
            scope.trafficType = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).not.toBeTruthy();
        }); 

        it("Should not set isRuleNotComplete to true if selectedProtocol is 'icmp' and fromPort is undefined when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = 'icmp';
            scope.fromPort = undefined;
            scope.trafficType = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).not.toBeTruthy();
        }); 

        it("Should not set isRuleNotComplete to true if selectedProtocol is 'icmp' and toPort is empty when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = 'icmp';
            scope.toPort = '';
            scope.trafficType = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).not.toBeTruthy();
        }); 

        it("Should not set isRuleNotComplete to true if selectedProtocol is 'icmp' and toPort is undefined when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = 'icmp';
            scope.toPort = undefined;
            scope.trafficType = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).not.toBeTruthy();
        }); 

        it("Should not set isRuleNotComplete to true if selectedProtocol is '-1' and fromPort is empty when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.fromPort = '';
            scope.trafficType = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).not.toBeTruthy();
        }); 

        it("Should not set isRuleNotComplete to true if selectedProtocol is '-1' and fromPort is undefined when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.fromPort = undefined;
            scope.trafficType = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).not.toBeTruthy();
        }); 

        it("Should not set isRuleNotComplete to true if selectedProtocol is '-1' and toPort is empty when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.toPort = '';
            scope.trafficType = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).not.toBeTruthy();
        }); 

        it("Should not set isRuleNotComplete to true if selectedProtocol is '-1' and toPort is undefined when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.toPort = undefined;
            scope.trafficType = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).not.toBeTruthy();
        }); 

        it("Should set isRuleNotComplete to true if trafficType is 'ip' and cidrIp is empty when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.trafficType = 'ip';
            scope.cidrIp = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).toBeTruthy();
        }); 

        it("Should set isRuleNotComplete to true if trafficType is 'ip' and cidrIp is undefined when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.trafficType = 'ip';
            scope.cidrIp = undefined;
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).toBeTruthy();
        }); 

        it("Should set isRuleNotComplete to true if trafficType is 'securitygroup' and groupName is empty when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.trafficType = 'securitygroup';
            scope.groupName = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).toBeTruthy();
        }); 

        it("Should set isRuleNotComplete to true if trafficType is 'securitygroup' and groupName is undefined when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.trafficType = 'securitygroup';
            scope.groupName = undefined;
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).toBeTruthy();
        }); 

        it("Should not set isRuleNotComplete to true if trafficType is not ['ip', 'securitygroup'] and cidrIp is empty when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.trafficType = '';
            scope.cidrIp = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).not.toBeTruthy();
        }); 

        it("Should not set isRuleNotComplete to true if trafficType is not ['ip', 'securitygroup'] and cidrIp is undefined when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.trafficType = '';
            scope.cidrIp = undefined;
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).not.toBeTruthy();
        }); 

        it("Should not set isRuleNotComplete to true if trafficType is not ['ip', 'securitygroup'] and groupName is empty when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.trafficType = '';
            scope.groupName = '';
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).not.toBeTruthy();
        }); 

        it("Should not set isRuleNotComplete to true if trafficType is not ['ip', 'securitygroup'] and groupName is undefined when checkRequiredInput is called", function() {
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.trafficType = '';
            scope.groupName = undefined;
            scope.checkRequiredInput();
            expect(scope.isRuleNotComplete).not.toBeTruthy();
        }); 
    });

    describe("Function setWatchers() Test", function() {

        var vpc = 'vpc-12345678';

        beforeEach(function() {
            setFixtures('<input id="csrf_token" name="csrf_token" type="hidden" value="2a06f17d6872143ed806a695caa5e5701a127ade">');
            scope.jsonEndpoint  = "securitygroup_json";
            scope.securityGroupVPC = vpc; 
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + vpc;
            httpBackend.expect('POST', scope.jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
            scope.internetProtocols = ["HOPOPT", "ICMP", "IGMP"];
        });

        it("Should call checkRequiredInput when selectedProtocol is updated", function() {
            spyOn(scope, 'checkRequiredInput');
            scope.setWatchers();
            scope.selectedProtocol = "icmp";
            scope.$apply();
            expect(scope.checkRequiredInput).toHaveBeenCalled();
        });

        it("Should set cidrIp to empty when selectedProtocol is updated and selectedProtocl is not '-1'", function() {
            scope.setWatchers();
            scope.selectedProtocol = "icmp";
            scope.$apply();
            expect(scope.cidrIp).toEqual('');
        });

        it("Should set cidrIp to '0.0.0.0/0' when selectedProtocol is updated and selectedProtocl is '-1'", function() {
            scope.setWatchers();
            scope.selectedProtocol = "-1";
            scope.$apply();
            expect(scope.cidrIp).toEqual('0.0.0.0/0');
        });

        it("Should call checkRequiredInput when customProtocol is updated", function() {
            spyOn(scope, 'checkRequiredInput');
            scope.setWatchers();
            scope.customProtocol = 12;
            scope.$apply();
            expect(scope.checkRequiredInput).toHaveBeenCalled();
        });

        it("Should set customProtocolDivClass to empty when customProtocol is cleared", function() {
            scope.customProtocol = 'ICMP';
            scope.setWatchers();
            scope.customProtocolDivClass = 'error';
            scope.customProtocol = '';
            scope.$apply();
            expect(scope.customProtocolDivClass).toEqual('');
        });

        it("Should set customProtocolDivClass to empty when customProtocol is updated and validated", function() {
            scope.setWatchers();
            scope.customProtocolDivClass = 'error';
            scope.customProtocol = 1;
            scope.$apply();
            expect(scope.customProtocolDivClass).toEqual('');
        });

        it("Should set customProtocolDivClass to 'error' when customProtocol is updated, but invalid", function() {
            scope.setWatchers();
            scope.customProtocolDivClass = '';
            scope.customProtocol = 'InvalidProtocol';
            scope.$apply();
            expect(scope.customProtocolDivClass).toEqual('error');
        });

        it("Should call setAddRuleButtonClass when isRuleNotComplete is updated", function() {
            spyOn(scope, 'setAddRuleButtonClass');
            scope.setWatchers();
            scope.isRuleNotComplete = true;
            scope.$apply();
            expect(scope.setAddRuleButtonClass).toHaveBeenCalled();
        });

        it("Should call setAddRuleButtonClass when customProtocolDivClass is updated", function() {
            spyOn(scope, 'setAddRuleButtonClass');
            scope.setWatchers();
            scope.customProtocolDivClass = 'error';
            scope.$apply();
            expect(scope.setAddRuleButtonClass).toHaveBeenCalled();
        });

        it("Should call checkRequiredInput when fromPort is updated", function() {
            spyOn(scope, 'checkRequiredInput');
            scope.setWatchers();
            scope.fromPort = 88;
            scope.$apply();
            expect(scope.checkRequiredInput).toHaveBeenCalled();
        });

        it("Should call checkRequiredInput when toPort is updated", function() {
            spyOn(scope, 'checkRequiredInput');
            scope.setWatchers();
            scope.toPort = 88;
            scope.$apply();
            expect(scope.checkRequiredInput).toHaveBeenCalled();
        });

        it("Should call checkRequiredInput when icmpRange is updated", function() {
            spyOn(scope, 'checkRequiredInput');
            scope.setWatchers();
            scope.icmpRange = 88;
            scope.$apply();
            expect(scope.checkRequiredInput).toHaveBeenCalled();
        });

        it("Should call checkRequiredInput when cidrIp is updated", function() {
            spyOn(scope, 'checkRequiredInput');
            scope.setWatchers();
            scope.cidrIp = '0.0.0.0/0';
            scope.$apply();
            expect(scope.checkRequiredInput).toHaveBeenCalled();
        });

        it("Should call checkForDuplicatedRules when cidrIp is updated", function() {
            spyOn(scope, 'checkForDuplicatedRules');
            scope.setWatchers();
            scope.cidrIp = '0.0.0.0/0';
            scope.$apply();
            expect(scope.checkForDuplicatedRules).toHaveBeenCalled();
        });

        it("Should call checkRequiredInput when groupName is updated", function() {
            spyOn(scope, 'checkRequiredInput');
            scope.setWatchers();
            scope.groupName = null;
            scope.$apply();
            expect(scope.checkRequiredInput).toHaveBeenCalled();
        });

        it("Should call checkForDuplicatedRules when groupName is updated", function() {
            spyOn(scope, 'checkForDuplicatedRules');
            scope.setWatchers();
            scope.groupName = null;
            scope.$apply();
            expect(scope.checkForDuplicatedRules).toHaveBeenCalled();
        });

        it("Should set hasInvalidOwner to false when groupName is updated", function() {
            scope.setWatchers();
            scope.groupName = null;
            scope.$apply();
            expect(scope.hasInvalidOwner).not.toBeTruthy();
        });

        it("Should set trafficType to 'securitygroup' when groupName is updated", function() {
            scope.setWatchers();
            scope.groupName = null;
            scope.$apply();
            expect(scope.trafficType).toEqual('securitygroup');
        });

        it("Should not set trafficType to 'securitygroup' when groupName is clearned", function() {
            scope.setWatchers();
            scope.trafficType = 'ip';
            scope.groupName = '';
            scope.$apply();
            expect(scope.trafficType).not.toEqual('securitygroup');
        });

        it("Should call checkRequiredInput when trafficType is updated", function() {
            spyOn(scope, 'checkRequiredInput');
            scope.setWatchers();
            scope.trafficType = 'ip';
            scope.$apply();
            expect(scope.checkRequiredInput).toHaveBeenCalled();
        });

        it("Should call checkForDuplicatedRules when trafficType is updated", function() {
            spyOn(scope, 'checkForDuplicatedRules');
            scope.setWatchers();
            scope.trafficType = 'ip';
            scope.$apply();
            expect(scope.checkForDuplicatedRules).toHaveBeenCalled();
        });

        it("Should call getAllSecurityGroups when securityGroupVPC is updated", function() {
            spyOn(scope, 'getAllSecurityGroups');
            scope.setWatchers();
            scope.securityGroupVPC = vpc;
            scope.$apply();
            expect(scope.getAllSecurityGroups).toHaveBeenCalledWith(scope.securityGroupVPC);
        });

        it("Should call checkRulesForDeletedSecurityGroups when securityGroupList is updated", function() {
            spyOn(scope, 'checkRulesForDeletedSecurityGroups');
            scope.setWatchers();
            scope.securityGroupList.push("newSecurityGroup");
            scope.$apply();
            expect(scope.checkRulesForDeletedSecurityGroups).toHaveBeenCalled();
        });

        it("Should not call checkRulesForDeletedSecurityGroups when securityGroupList is cleared", function() {
            spyOn(scope, 'checkRulesForDeletedSecurityGroups');
            scope.setWatchers();
            scope.securityGroupList = [];
            scope.$apply();
            expect(scope.checkRulesForDeletedSecurityGroups).not.toHaveBeenCalled();
        });

        it("Should call setAddRuleButtonClass when hasDuplicatedRule is updated", function() {
            spyOn(scope, 'setAddRuleButtonClass');
            scope.setWatchers();
            scope.hasDuplicatedRule = true;
            scope.$apply();
            expect(scope.setAddRuleButtonClass).toHaveBeenCalled();
        });

        it("Should call getAllSecurityGroups when initModal is triggered", function() {
            spyOn(scope, 'getAllSecurityGroups');
            scope.setWatchers();
            scope.$broadcast('initModal');
            scope.$apply();
            expect(scope.getAllSecurityGroups).toHaveBeenCalledWith(scope.securityGroupVPC);
        });

        it("Should call adjustIPProtocolOptions when updateVPC is triggered", function() {
            spyOn(scope, 'adjustIPProtocolOptions');
            scope.setWatchers();
            httpBackend.flush();
            httpBackend.verifyNoOutstandingExpectation();
            httpBackend.verifyNoOutstandingRequest();
            scope.jsonEndpoint = "localhost/vpc";
            var newVPC = 'vpc-11111111';
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + newVPC; 
            httpBackend.expect('POST', scope.jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
            scope.$broadcast('updateVPC', newVPC);
            scope.$apply();
            expect(scope.adjustIPProtocolOptions).toHaveBeenCalled();
        });

        it("Should not call adjustIPProtocolOptions if vpc is undefined when updateVPC is triggered", function() {
            spyOn(scope, 'adjustIPProtocolOptions');
            scope.setWatchers();
            httpBackend.flush();
            httpBackend.verifyNoOutstandingExpectation();
            httpBackend.verifyNoOutstandingRequest();
            scope.jsonEndpoint = "localhost/vpc";
            var newVPC = '';
            newVPC = undefined;
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + newVPC; 
            httpBackend.expect('POST', scope.jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
            scope.$broadcast('updateVPC', newVPC);
            scope.$apply();
            expect(scope.adjustIPProtocolOptions).not.toHaveBeenCalled();
        });

        it("Should not call adjustIPProtocolOptions if vpc is the same as previous when updateVPC is triggered", function() {
            spyOn(scope, 'adjustIPProtocolOptions');
            scope.setWatchers();
            httpBackend.flush();
            httpBackend.verifyNoOutstandingExpectation();
            httpBackend.verifyNoOutstandingRequest();
            scope.jsonEndpoint = "localhost/vpc";
            var newVPC = vpc;
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + newVPC; 
            httpBackend.expect('POST', scope.jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
            scope.$broadcast('updateVPC', newVPC);
            scope.$apply();
            expect(scope.adjustIPProtocolOptions).not.toHaveBeenCalled();
        });

        it("Should update securityGroupVPC when updateVPC is triggered", function() {
            scope.setWatchers();
            httpBackend.flush();
            httpBackend.verifyNoOutstandingExpectation();
            httpBackend.verifyNoOutstandingRequest();
            scope.jsonEndpoint = "localhost/vpc";
            var newVPC = 'vpc-11111111';
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + newVPC; 
            httpBackend.expect('POST', scope.jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
            scope.$broadcast('updateVPC', newVPC);
            scope.$apply();
            expect(scope.securityGroupVPC).toEqual(newVPC);
        });

        it("Should not call selectRuleType if vpc is not None when updateVPC is triggered", function() {
            spyOn(scope, 'selectRuleType');
            scope.setWatchers();
            httpBackend.flush();
            httpBackend.verifyNoOutstandingExpectation();
            httpBackend.verifyNoOutstandingRequest();
            scope.jsonEndpoint = "localhost/vpc";
            var newVPC = vpc;
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + newVPC; 
            httpBackend.expect('POST', scope.jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
            scope.$broadcast('updateVPC', newVPC);
            scope.$apply();
            expect(scope.selectRuleType).not.toHaveBeenCalled();
        });

        it("Should call selectRuleType if vpc is None when updateVPC is triggered", function() {
            spyOn(scope, 'selectRuleType');
            scope.setWatchers();
            httpBackend.flush();
            httpBackend.verifyNoOutstandingExpectation();
            httpBackend.verifyNoOutstandingRequest();
            scope.jsonEndpoint = "localhost/vpc";
            var newVPC = 'None';
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + newVPC; 
            httpBackend.expect('POST', scope.jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
            scope.$broadcast('updateVPC', newVPC);
            scope.$apply();
            expect(scope.selectRuleType).toHaveBeenCalled();
        });

        it("Should call clearRules if securitygroup_vpc_network select element exists when updateVPC is triggered", function() {
            spyOn(scope, 'clearRules');
            scope.setWatchers();
            httpBackend.flush();
            httpBackend.verifyNoOutstandingExpectation();
            httpBackend.verifyNoOutstandingRequest();
            setFixtures('<select id="securitygroup_vpc_network"></select>');
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/vpc", "protocols_json_endpoint": "localhost/ipprotocol"}');
            var jsonEndpoint = "localhost/vpc";
            var newVPC = 'vpc-11111111';
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + newVPC; 
            httpBackend.expect('POST', jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
            var internetProtocolsJsonEndpoint  = "localhost/ipprotocol";
            httpBackend.expect('POST', internetProtocolsJsonEndpoint, 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade')
                .respond(200, {
                    "success": true,
                    "results": angular.toJson({"internet_protocols": [[0, "HOPOPT"], [1, "ICMP"], [2, "IGMP"]]}) 
                });
            scope.$broadcast('updateVPC', newVPC);
            expect(scope.clearRules).toHaveBeenCalled();
        });

        it("Should not call clearRules if securitygroup_vpc_network select element does not exist when updateVPC is triggered", function() {
            spyOn(scope, 'clearRules');
            scope.setWatchers();
            httpBackend.flush();
            httpBackend.verifyNoOutstandingExpectation();
            httpBackend.verifyNoOutstandingRequest();
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/vpc", "protocols_json_endpoint": "localhost/ipprotocol"}');
            var jsonEndpoint = "localhost/vpc";
            var newVPC = 'vpc-11111111';
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + newVPC; 
            httpBackend.expect('POST', jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
            var internetProtocolsJsonEndpoint  = "localhost/ipprotocol";
            httpBackend.expect('POST', internetProtocolsJsonEndpoint, 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade')
                .respond(200, {
                    "success": true,
                    "results": angular.toJson({"internet_protocols": [[0, "HOPOPT"], [1, "ICMP"], [2, "IGMP"]]}) 
                });
            scope.$broadcast('updateVPC', newVPC);
            expect(scope.clearRules).not.toHaveBeenCalled();
        });

        it("Should call addDefaultOutboundRule if securitygroup_vpc_network select element exists and securityGroupVPC is not None when updateVPC is triggered", function() {
            spyOn(scope, 'addDefaultOutboundRule');
            scope.setWatchers();
            httpBackend.flush();
            httpBackend.verifyNoOutstandingExpectation();
            httpBackend.verifyNoOutstandingRequest();
            setFixtures('<select id="securitygroup_vpc_network"></select>');
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/vpc", "protocols_json_endpoint": "localhost/ipprotocol"}');
            var jsonEndpoint = "localhost/vpc";
            var newVPC = 'vpc-11111111';
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + newVPC; 
            httpBackend.expect('POST', jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
            var internetProtocolsJsonEndpoint  = "localhost/ipprotocol";
            httpBackend.expect('POST', internetProtocolsJsonEndpoint, 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade')
                .respond(200, {
                    "success": true,
                    "results": angular.toJson({"internet_protocols": [[0, "HOPOPT"], [1, "ICMP"], [2, "IGMP"]]}) 
                });
            scope.$broadcast('updateVPC', newVPC);
            expect(scope.addDefaultOutboundRule).toHaveBeenCalled();
        });

        it("Should not call addDefaultOutboundRule if securitygroup_vpc_network select element exists and securityGroupVPC is None when updateVPC is triggered", function() {
            spyOn(scope, 'addDefaultOutboundRule');
            scope.setWatchers();
            httpBackend.flush();
            httpBackend.verifyNoOutstandingExpectation();
            httpBackend.verifyNoOutstandingRequest();
            setFixtures('<select id="securitygroup_vpc_network"></select>');
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/vpc", "protocols_json_endpoint": "localhost/ipprotocol"}');
            var jsonEndpoint = "localhost/vpc";
            var newVPC = 'None';
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + newVPC; 
            httpBackend.expect('POST', jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
            var internetProtocolsJsonEndpoint  = "localhost/ipprotocol";
            httpBackend.expect('POST', internetProtocolsJsonEndpoint, 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade')
                .respond(200, {
                    "success": true,
                    "results": angular.toJson({"internet_protocols": [[0, "HOPOPT"], [1, "ICMP"], [2, "IGMP"]]}) 
                });
            scope.$broadcast('updateVPC', newVPC);
            expect(scope.addDefaultOutboundRule).not.toHaveBeenCalled();
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
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + vpc;
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

        it("Should call getGroupIdByName() if trafficType is 'securitygroup' and groupName is defined", function() {
            spyOn(scope, 'getGroupIdByName');
            scope.trafficType = 'securitygroup';
            scope.groupName = "12345678/my group";
            scope.createRuleArrayBlock();
            expect(scope.getGroupIdByName).toHaveBeenCalled();
        });

        it("Should not call getGroupIdByName() if trafficType is 'securitygroup' and groupName is null", function() {
            spyOn(scope, 'getGroupIdByName');
            scope.trafficType = 'securitygroup';
            scope.groupName = null;
            scope.createRuleArrayBlock();
            expect(scope.getGroupIdByName).not.toHaveBeenCalled();
        });

        it("Should not call getGroupIdByName() if trafficType is not 'securitygroup'", function() {
            spyOn(scope, 'getGroupIdByName');
            scope.trafficType = 'ip';
            scope.groupName = null;
            scope.createRuleArrayBlock();
            expect(scope.getGroupIdByName).not.toHaveBeenCalled();
        });

        it("Should call adjustIpProtocol() when createRuleArrayBlock() is called", function() {
            spyOn(scope, 'adjustIpProtocol');
            scope.createRuleArrayBlock();
            expect(scope.adjustIpProtocol).toHaveBeenCalled();
        });

        it("Should call getCustomProtocolName() when createRuleArrayBlock() is called", function() {
            spyOn(scope, 'getCustomProtocolName');
            scope.createRuleArrayBlock();
            expect(scope.getCustomProtocolName).toHaveBeenCalledWith(scope.customProtocol);
        });

        it("Should return the matching group_id value when createRuleArrayBlock() is returned", function() {
            scope.fromPort = 22;
            scope.toPort = 22;
            scope.ipProtocol = 'tcp';
            scope.trafficType = 'securitygroup';
            scope.cidrIp = '0.0.0.0/0'; 
            scope.ruleType = 'inbound';
            scope.groupName = "1234/group2";
            scope.securityGroupList = [{"name": "group1", "id": "sg-00000000"}, {"name": "group2", "id": "sg-12345678"}];
            var output = scope.createRuleArrayBlock();
            expect(output).toEqual({
                'from_port': 22,
                'to_port': 22,
                'ip_protocol': 'tcp',
                'custom_protocol': undefined,
                'grants': [{
                    'cidr_ip': null,
                    'group_id': 'sg-12345678',
                    'name': 'group2',
                    'owner_id': '1234' 
                }],
                'rule_type': 'inbound',
                'fresh': 'new'
            });
        });

        it("Should return owner_id to be null if groupName does not contain '/' when createRuleArrayBlock() is returned", function() {
            scope.fromPort = 22;
            scope.toPort = 22;
            scope.ipProtocol = 'tcp';
            scope.trafficType = 'securitygroup';
            scope.cidrIp = '0.0.0.0/0'; 
            scope.ruleType = 'inbound';
            scope.groupName = "group1";
            scope.securityGroupList = [{"name": "group1", "id": "sg-00000000"}, {"name": "group2", "id": "sg-12345678"}];
            var output = scope.createRuleArrayBlock();
            expect(output).toEqual({
                'from_port': 22,
                'to_port': 22,
                'ip_protocol': 'tcp',
                'custom_protocol': undefined,
                'grants': [{
                    'cidr_ip': null,
                    'group_id': 'sg-00000000',
                    'name': 'group1',
                    'owner_id': null 
                }],
                'rule_type': 'inbound',
                'fresh': 'new'
            });
        });

        it("Should return group_id to be null if trafficType is not 'securitygroup' when createRuleArrayBlock() is returned", function() {
            scope.fromPort = 22;
            scope.toPort = 22;
            scope.ipProtocol = 'tcp';
            scope.trafficType = 'ip';
            scope.cidrIp = '0.0.0.0/0'; 
            scope.ruleType = 'inbound';
            scope.groupName = "group1";
            scope.securityGroupList = [{"name": "group1", "id": "sg-00000000"}, {"name": "group2", "id": "sg-12345678"}];
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

        it("Should return the matching cidr_ip value if trafficType is 'ip' when createRuleArrayBlock() is returned", function() {
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

        it("Should return cidr_ip value to be null if trafficType is not 'ip' when createRuleArrayBlock() is returned", function() {
            scope.fromPort = 22;
            scope.toPort = 22;
            scope.ipProtocol = 'tcp';
            scope.trafficType = 'securitygroup';
            scope.cidrIp = '0.0.0.0/0'; 
            scope.ruleType = 'inbound';
            var output = scope.createRuleArrayBlock();
            expect(output).toEqual({
                'from_port': 22,
                'to_port': 22,
                'ip_protocol': 'tcp',
                'custom_protocol': undefined,
                'grants': [{
                    'cidr_ip': null,
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

    describe("Event initModal Test", function() {

        it("Should call getAllSecurityGroupVPC when initModal is called", function() {
            spyOn(scope, 'getAllSecurityGroups');
            scope.setWatchers();
            scope.securityGroupVPC = "vpc-12345678";
            scope.$broadcast('initModal');
            expect(scope.getAllSecurityGroups).toHaveBeenCalledWith('vpc-12345678');
        });
    });

    describe("Event updateVPC Test", function() {

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
            scope.securityGroupVPC = 'None';
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

    describe("Function setAddRuleButtonClass() Test", function() {

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
            scope.hasDuplicatedRule = false; 
            scope.customProtocolDivClass = '';
            scope.setAddRuleButtonClass(); 
            expect(scope.addRuleButtonClass).toEqual('');
        });
    });

    describe("Function checkRulesForDeletedSecurityGroups Test", function() {

        beforeEach(function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}, {"to_port":"4000","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"4000"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":"1234","group_id":"sg-12345678","cidr_ip":"0.0.0.0/0","name":"group2"}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
        });

        it("Should emit 'invalidRulesWarning' with the invalid rules array when checkRulesForDeletedSecurityGroups is called", function() {
            spyOn(scope, '$emit');
            scope.checkRulesForDeletedSecurityGroups(); 
            expect(scope.$emit).toHaveBeenCalledWith('invalidRulesWarning',[  ], [ { to_port : '22', grants : [ { owner_id : '1234', group_id : 'sg-12345678', cidr_ip : '0.0.0.0/0', name : 'group2' } ], ip_protocol : 'tcp', from_port : '22' } ]);
        });
    });

    describe("Function checkForDuplicatedRules Test", function() {

        beforeEach(function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}, {"to_port":"4000","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"4000"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":"1234","group_id":"sg-12345678","cidr_ip":"0.0.0.0/0","name":"group2"}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
        });

        it("Should call createRuleArrayBlock when checkForDuplicatedRules is called", function() {
            spyOn(scope, 'createRuleArrayBlock').and.callThrough();
            scope.fromPort = 3389;
            scope.toPort = 3389;
            scope.ipProtocol = 'tcp';
            scope.trafficType = 'ip';
            scope.cidrIp = '10.5.1.66/32'; 
            scope.ruleType = 'inbound';
            scope.groupName = "null";
            scope.checkForDuplicatedRules();
            expect(scope.createRuleArrayBlock).toHaveBeenCalled();
        });

        it("Should set hasDuplicatedRule to be true if the new rule already exists when checkForDuplicatedRules is called", function() { 
            scope.fromPort = 3389;
            scope.toPort = 3389;
            scope.ipProtocol = 'tcp';
            scope.trafficType = 'ip';
            scope.cidrIp = '10.5.1.66/32'; 
            scope.ruleType = 'inbound';
            scope.groupName = "null";
            scope.checkForDuplicatedRules();
            expect(scope.hasDuplicatedRule).toBeTruthy();
        });

        it("Should set hasDuplicatedRule to be false if the new rule does not already exist when checkForDuplicatedRules is called", function() { 
            scope.fromPort = 4000;
            scope.toPort = 3389;
            scope.ipProtocol = 'tcp';
            scope.trafficType = 'ip';
            scope.cidrIp = '10.5.1.66/32'; 
            scope.ruleType = 'inbound';
            scope.groupName = "null";
            scope.checkForDuplicatedRules();
            expect(scope.hasDuplicatedRule).not.toBeTruthy();
        });

        it("Should set hasDuplicatedRule to be true if the new egress rule already exists when checkForDuplicatedRules is called", function() { 
            scope.fromPort = 22;
            scope.toPort = 22;
            scope.ipProtocol = 'tcp';
            scope.trafficType = 'securitygroup';
            scope.cidrIp = '0.0.0.0/0'; 
            scope.ruleType = 'outbound';
            scope.groupName = "group2";
            scope.securityGroupList = [{"name": "group1", "id": "sg-00000000"}, {"name": "group2", "id": "sg-12345678"}];
            scope.checkForDuplicatedRules();
            expect(scope.hasDuplicatedRule).toBeTruthy();
        });

        it("Should set hasDuplicatedRule to be false if the new egress rule does not already exists when checkForDuplicatedRules is called", function() { 
            scope.fromPort = 22;
            scope.toPort = 22;
            scope.ipProtocol = 'tcp';
            scope.trafficType = 'securitygroup';
            scope.cidrIp = '0.0.0.0/0'; 
            scope.ruleType = 'outbound';
            scope.groupName = "group1";
            scope.securityGroupList = [{"name": "group1", "id": "sg-00000000"}, {"name": "group2", "id": "sg-12345678"}];
            scope.checkForDuplicatedRules();
            expect(scope.hasDuplicatedRule).not.toBeTruthy();
        });
    });

    describe("Function compareRules Test", function() {

        it("Should return true if trafficType is 'ip' and the rules are the same when compareRules is called", function() {
            var block1 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp"};
            scope.trafficType = 'ip';
            var output = scope.compareRules(block1, block1);
            expect(output).toBeTruthy();
        });

        it("Should return false if the rules have different 'from_port' when compareRules is called", function() {
            var block1 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp"};
            var block2 = {"from_port":"4000","to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp"};
            var output = scope.compareRules(block1, block2);
            expect(output).not.toBeTruthy();
        });

        it("Should return false if the rules have different 'to_port' when compareRules is called", function() {
            var block1 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp"};
            var block2 = {"from_port":"3389","to_port":"4000","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp"};
            var output = scope.compareRules(block1, block2);
            expect(output).not.toBeTruthy();
        });

        it("Should return false if the rules have different 'ip_protocol' when compareRules is called", function() {
            var block1 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp"};
            var block2 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"udp"};
            var output = scope.compareRules(block1, block2);
            expect(output).not.toBeTruthy();
        });

        it("Should return false if trafficType is 'ip' and the first rule has 'cidr_ip' value of null when compareRules is called", function() {
            var block1 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":null,"name":null}],"ip_protocol":"tcp"};
            var block2 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":null,"name":null}],"ip_protocol":"tcp"};
            scope.trafficType = 'ip';
            var output = scope.compareRules(block1, block2);
            expect(output).not.toBeTruthy();
        });

        it("Should return false if trafficType is 'ip' and the rules have different 'cidr_ip' values when compareRules is called", function() {
            var block1 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.1.1.1./32","name":null}],"ip_protocol":"tcp"};
            var block2 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp"};
            scope.trafficType = 'ip';
            var output = scope.compareRules(block1, block2);
            expect(output).not.toBeTruthy();
        });

        it("Should return true if trafficType is not 'ip' and the rules are the same when compareRules is called", function() {
            var block1 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":"1234","group_id":"sg-12345678","cidr_ip":null,"name": "myGroup"}],"ip_protocol":"tcp"};
            scope.trafficType = 'securitygroup';
            var output = scope.compareRules(block1, block1);
            expect(output).toBeTruthy();
        });

        it("Should return false if trafficType is not 'ip' and the first rules has null group name when compareRules is called", function() {
            var block1 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":"1234","group_id":"sg-12345678","cidr_ip":null,"name": null}],"ip_protocol":"tcp"};
            var block2 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":"1234","group_id":"sg-12345678","cidr_ip":null,"name": null}],"ip_protocol":"tcp"};
            scope.trafficType = 'securitygroup';
            var output = scope.compareRules(block1, block2);
            expect(output).not.toBeTruthy();
        });

        it("Should return false if trafficType is not 'ip' and the rules have different group names when compareRules is called", function() {
            var block1 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":"1234","group_id":"sg-12345678","cidr_ip":null,"name": "myGroup1"}],"ip_protocol":"tcp"};
            var block2 = {"from_port":"3389","to_port":"3389","grants":[{"owner_id":"1234","group_id":"sg-12345678","cidr_ip":null,"name": "myGroup2"}],"ip_protocol":"tcp"};
            scope.trafficType = 'securitygroup';
            var output = scope.compareRules(block1, block2);
            expect(output).not.toBeTruthy();
        });
    });

    describe("Function removeRule Test", function() {

        beforeEach(function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}, {"to_port":"4000","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"4000"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
        });

        it("Should call preventDefault when removeRule is called", function() {
            var event ={"preventDefault": function(){}};
            spyOn(event, 'preventDefault');
            scope.removeRule(1, event); 
            expect(event.preventDefault).toHaveBeenCalled();
        });

        it("Should call syncRules when removeRule is called", function() {
            spyOn(scope, 'syncRules');
            scope.removeRule(1, {"preventDefault": function(){}}); 
            expect(scope.syncRules).toHaveBeenCalled();
        });

        it("Should emit securityGroupUpdate when removeRule is called", function() {
            spyOn(scope, '$emit');
            scope.removeRule(1, {"preventDefault": function(){}});
            expect(scope.$emit).toHaveBeenCalledWith('securityGroupUpdate');
        });

        it("Should remove the item in rulesArray when removeRule is called with index", function() {
            scope.ruleType = 'inbound';
            expect(scope.rulesArray.length).toEqual(2);
            expect(scope.rulesArray[0].to_port).toEqual("3389");
            expect(scope.rulesArray[1].to_port).toEqual("4000");
            scope.removeRule(1, {"preventDefault": function(){}}); 
            expect(scope.rulesArray.length).toEqual(1);
            expect(scope.rulesArray[0].to_port).toEqual("3389");
            expect(scope.rulesArray[1]).toEqual(undefined);
        });

        it("Should remove the item in rulesEgressArray when removeRule is called with index", function() {
            scope.ruleType = 'outbound';
            expect(scope.rulesEgressArray.length).toEqual(1);
            expect(scope.rulesEgressArray[0].to_port).toEqual("22");
            scope.removeRule(0, {"preventDefault": function(){}}); 
            expect(scope.rulesEgressArray.length).toEqual(0);
            expect(scope.rulesEgressArray[1]).toEqual(undefined);
        });
    });

    describe("Function adjustIpProtocol Test", function() {

        beforeEach(function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}, {"to_port":"4000","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"4000"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
        });

        it("Should update fromPort and toPort if selectedProtocol is 'icmp' when adjustIpProtocol is called", function() {
            scope.selectedProtocol = 'icmp';
            scope.icmpRange = '22';
            scope.adjustIpProtocol();
            expect(scope.fromPort).toEqual('22');
            expect(scope.toPort).toEqual('22');
        });

        it("Should update ipProtocol to 'icmp' if selectedProtocol is 'icmp' when adjustIpProtocol is called", function() {
            scope.selectedProtocol = 'icmp';
            scope.icmpRange = '22';
            scope.adjustIpProtocol();
            expect(scope.ipProtocol).toEqual('icmp');
        });

        it("Should update ipProtocol to 'udp' if selectedProtocol is 'udp' when adjustIpProtocol is called", function() {
            scope.selectedProtocol = 'udp';
            scope.adjustIpProtocol();
            expect(scope.ipProtocol).toEqual('udp');
        });

        it("Should update ipProtocol to '-1' if selectedProtocol is '-1' when adjustIpProtocol is called", function() {
            scope.selectedProtocol = '-1';
            scope.adjustIpProtocol();
            expect(scope.ipProtocol).toEqual('-1');
        });

        it("Should update fromPort and toPort to null if selectedProtocol is '-1' when adjustIpProtocol is called", function() {
            scope.selectedProtocol = '-1';
            scope.adjustIpProtocol();
            expect(scope.fromPort).toEqual(null);
            expect(scope.toPort).toEqual(null);
        });

        it("Should update fromPort and toPort to null if selectedProtocol is 'custom' when adjustIpProtocol is called", function() {
            scope.selectedProtocol = 'custom';
            scope.adjustIpProtocol();
            expect(scope.fromPort).toEqual(null);
            expect(scope.toPort).toEqual(null);
        });

        it("Should update ipProtocol to customProtocol if selectedProtocol is 'custom' and customProtocol is a number when adjustIpProtocol is called", function() {
            scope.selectedProtocol = 'custom';
            scope.customProtocol = 10;
            scope.ipProtocol = 'icmp';
            scope.adjustIpProtocol();
            expect(scope.ipProtocol).toEqual(10);
        });

        it("Should call getCustomProtocolNumber if selectedProtocol is 'custom' and customProtocol is not a number when adjustIpProtocol is called", function() {
            spyOn(scope, 'getCustomProtocolNumber');
            scope.selectedProtocol = 'custom';
            scope.customProtocol = 'IGMP';
            scope.ipProtocol = 'icmp';
            scope.internetProtocols = ["HOPOPT", "ICMP", "IGMP"];
            scope.adjustIpProtocol();
            expect(scope.getCustomProtocolNumber).toHaveBeenCalledWith(scope.customProtocol);
        });

        it("Should update ipProtocol to translated custom protocol number if selectedProtocol is 'custom' and customProtocol is not a number when adjustIpProtocol is called", function() {
            scope.selectedProtocol = 'custom';
            scope.customProtocol = 'IGMP';
            scope.ipProtocol = 'icmp';
            scope.internetProtocols = ["HOPOPT", "ICMP", "IGMP"];
            scope.adjustIpProtocol();
            expect(scope.ipProtocol).toEqual(2);
        });

        it("Should update ipProtocol to 'tcp' if selectedProtocol is not ['icmp', 'udp', '-1', 'custom'] when adjustIpProtocol is called", function() {
            scope.selectedProtocol = 'unknown';
            scope.adjustIpProtocol();
            expect(scope.ipProtocol).toEqual('tcp');
        });
    });

    describe("Function addRule Test", function() {

        beforeEach(function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
        });

        it("Should call preventDefault when addRule is called", function() {
            var event ={"preventDefault": function(){}};
            spyOn(event, 'preventDefault');
            scope.addRule(event); 
            expect(event.preventDefault).toHaveBeenCalled();
        });

        it("Should call checkRequiredInput when addRule is called", function() {
            spyOn(scope, 'checkRequiredInput');
            scope.addRule({"preventDefault": function(){}}); 
            expect(scope.checkRequiredInput).toHaveBeenCalled();
        });

        it("Should return false if isRuleNotComplete is false when addRule is called", function() {
            scope.isRuleNotComplete  = false;
            var output = scope.addRule({"preventDefault": function(){}}); 
            expect(output).not.toBeTruthy();
        });

        it("Should return false if hasDuplicatedRule is false when addRule is called", function() {
            scope.isRuleNotComplete  = true;
            scope.hasDuplicatedRule = false;
            var output = scope.addRule({"preventDefault": function(){}}); 
            expect(output).not.toBeTruthy();
        });

        it("Should return false if hasInvalidOwner is false when addRule is called", function() {
            scope.isRuleNotComplete  = true;
            scope.hasDuplicatedRule = true;
            scope.hasInvalidOwner = false;
            var output = scope.addRule({"preventDefault": function(){}}); 
            expect(output).not.toBeTruthy();
        });

        it("Should update rulesArray if ruleType is 'inbound' when addRule is called", function() {
            scope.isRuleNotComplete  = false;
            scope.hasDuplicatedRule = false;
            scope.hasInvalidOwner = false;
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.trafficType = '';
            scope.cidrIp = '';
            scope.ruleType = 'inbound';
            expect(scope.rulesArray.length).toEqual(1);
            scope.addRule({"preventDefault": function(){}}); 
            expect(scope.rulesArray.length).toEqual(2);
        });

        it("Should update rulesEgressArray if ruleType is 'outbound' when addRule is called", function() {
            scope.isRuleNotComplete  = false;
            scope.hasDuplicatedRule = false;
            scope.hasInvalidOwner = false;
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.trafficType = '';
            scope.cidrIp = '';
            scope.ruleType = 'outbound';
            expect(scope.rulesEgressArray.length).toEqual(1);
            scope.addRule({"preventDefault": function(){}}); 
            expect(scope.rulesEgressArray.length).toEqual(2);
        });

        it("Should call syncRules when addRule is executed cleanly", function() {
            spyOn(scope, 'syncRules');
            scope.isRuleNotComplete  = false;
            scope.hasDuplicatedRule = false;
            scope.hasInvalidOwner = false;
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.trafficType = '';
            scope.cidrIp = '';
            scope.addRule({"preventDefault": function(){}}); 
            expect(scope.syncRules).toHaveBeenCalled();
        });

        it("Should emit securityGroupUpdate when addRule is executed cleanly", function() {
            spyOn(scope, '$emit');
            scope.isRuleNotComplete  = false;
            scope.hasDuplicatedRule = false;
            scope.hasInvalidOwner = false;
            scope.hasDuplicatedRule = false;
            scope.selectedProtocol = '-1';
            scope.trafficType = '';
            scope.cidrIp = '';
            scope.addRule({"preventDefault": function(){}}); 
            expect(scope.$emit).toHaveBeenCalledWith('securityGroupUpdate');
        });

        it("Should remove 'error' class from 'ng-hide' class element when addRule is called", function() {

            setFixtures('<div class="error ng-hide"></div>');
            scope.addRule({"preventDefault": function(){}}); 
            expect($('.ng-hide').hasClass()).not.toBeTruthy(); 
        });
    });

    describe("Function cancelRule Test", function() {

        it("Should call preventDefault when cancelRule is called", function() {
            var event ={"preventDefault": function(){}};
            spyOn(event, 'preventDefault');
            scope.cancelRule(event); 
            expect(event.preventDefault).toHaveBeenCalled();
        });

        it("Should call resetValues when cancelRule is called", function() {
            spyOn(scope, 'resetValues');
            scope.cancelRule({"preventDefault": function(){}}); 
            expect(scope.resetValues).toHaveBeenCalled();
        });
    });

    describe("Function setPorts Test", function() {

        it("Should update fromPort and toPort when setPorts is called with integer value", function() {
            scope.fromPort = '';
            scope.toPort = '';
            scope.setPorts(22); 
            expect(scope.fromPort).toEqual(22);
            expect(scope.toPort).toEqual(22);
        });

        it("Should update fromPort and toPort to '' when setPorts is called with non-integer value", function() {
            scope.fromPort = 22;
            scope.toPort = 22;
            scope.setPorts('myString'); 
            expect(scope.fromPort).toEqual('');
            expect(scope.toPort).toEqual('');
        });

        it("Should set groupname-select to selectedIndex to -1  when setPorts is called", function() {
            scope.setPorts(22); 
            var index = $('#groupname-select').prop('selectedIndex');
            expect(index).toEqual(-1);
        });

        it("Should call cleanupSelections when setPorts is called", function() {
            spyOn(scope, 'cleanupSelections');
            scope.setPorts(22); 
            expect(scope.cleanupSelections).toHaveBeenCalled();
        });
    });

    describe("Function getGroupIdByName Test", function() {

        beforeEach(function() {
            scope.securityGroupList = [{"name": "group1", "id": "sg-00000000"}, {"name": "group2", "id": "sg-12345678"}];
        });

        it("Should return the matching id  when getGroupIdByName is called with group name", function() {
            var id = scope.getGroupIdByName('group2'); 
            expect(id).toEqual('sg-12345678');
        });

        it("Should return null when getGroupIdByName is called with the group name that has no match", function() {
            var id = scope.getGroupIdByName('group3'); 
            expect(id).toEqual(null);
        });
    });

    describe("Function openToAllAddresses Test", function() {

        it("Should set cidrIp to '0.0.0.0/0' when openToAllAddresses is called", function() {
            scope.cidrIp = '';
            scope.openToAllAddresses(); 
            expect(scope.cidrIp).toEqual('0.0.0.0/0');
        });
    });

    describe("Function useMyIP Test", function() {

        it("Should set cidrIp to <ip>/32 when useMyIP is called with <ip> input", function() {
            scope.cidrIp = '';
            scope.useMyIP('172.68.1.1'); 
            expect(scope.cidrIp).toEqual('172.68.1.1/32');
        });
    });

    describe("Function addDefaultOutboundRule Test", function() {

        beforeEach(function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
        });

        it("Should preserve ruleType value to 'inbound' after addDefaultOutboundRule is called", function() {
            scope.ruleType = 'inbound';
            scope.addDefaultOutboundRule(); 
            expect(scope.ruleType).toEqual('inbound');
        });

        it("Should preserve ruleType value to 'outbound' after addDefaultOutboundRule is called", function() {
            scope.ruleType = 'outbound';
            scope.addDefaultOutboundRule(); 
            expect(scope.ruleType).toEqual('outbound');
        });

        it("Should call checkForDuplicatedRules when addDefaultOutboundRule is called", function() {
            spyOn(scope, 'checkForDuplicatedRules');
            scope.addDefaultOutboundRule(); 
            expect(scope.checkForDuplicatedRules).toHaveBeenCalled();
        });

        it("Should call resetValues when addDefaultOutboundRule is called", function() {
            spyOn(scope, 'resetValues');
            scope.addDefaultOutboundRule(); 
            expect(scope.resetValues).toHaveBeenCalled();
        });

        it("Should call syncRules when addDefaultOutboundRule is called", function() {
            spyOn(scope, 'syncRules');
            scope.addDefaultOutboundRule(); 
            expect(scope.syncRules).toHaveBeenCalled();
        });

        it("Should call createRuleArrayBlock if the default rule doesn't exist when addDefaultOutboundRule is called", function() {
            spyOn(scope, 'createRuleArrayBlock').and.callThrough();
            scope.addDefaultOutboundRule(); 
            expect(scope.createRuleArrayBlock).toHaveBeenCalled();
        });

        it("Should update rulesEgressArray if the default rule doesn't exist when addDefaultOutboundRule is called", function() {
            expect(scope.rulesEgressArray.length).toEqual(1);
            scope.addDefaultOutboundRule(); 
            expect(scope.rulesEgressArray.length).toEqual(2);
        });

        it("Should not update rulesEgressArray if the default rule already exists when addDefaultOutboundRule is called", function() {
            scope.rulesEgressArray.push({
                'from_port': null,
                'to_port': null,
                'ip_protocol': '-1',
                'custom_protocol': undefined,
                'grants': [{
                    'cidr_ip': '0.0.0.0/0',
                    'group_id': null,
                    'name': null,
                    'owner_id': null 
                }],
                'rule_type': 'outbound'
            });
            expect(scope.rulesEgressArray.length).toEqual(2);
            scope.addDefaultOutboundRule(); 
            expect(scope.rulesEgressArray.length).toEqual(2);
        });
    });

    describe("Function selectRuleType Test", function() {

        it("Should update inboundButtonClass to 'active' and outboundButtonClass to 'inactive' when selectRuleType is called with 'inbound'", function() {
            scope.selectRuleType('inbound');
            expect(scope.inboundButtonClass).toEqual('active');
            expect(scope.outboundButtonClass).toEqual('inactive');
        });

        it("Should update inboundButtonClass to 'inactive' and outboundButtonClass to 'active' when selectRuleType is called with 'outbound'", function() {
            scope.selectRuleType('outbound');
            expect(scope.inboundButtonClass).toEqual('inactive');
            expect(scope.outboundButtonClass).toEqual('active');
        });
    });

    describe("Function adjustIPProtocolOptions Test", function() {

        it("Should call removeAllTrafficRuleOption when adjustIPProtocolOptions is called", function() {
            spyOn(scope, 'removeAllTrafficRuleOption');
            scope.adjustIPProtocolOptions(); 
            expect(scope.removeAllTrafficRuleOption).toHaveBeenCalled();
        });

        it("Should call removeCustomProtocolRuleOption when adjustIPProtocolOptions is called", function() {
            spyOn(scope, 'removeCustomProtocolRuleOption');
            scope.adjustIPProtocolOptions(); 
            expect(scope.removeCustomProtocolRuleOption).toHaveBeenCalled();
        });

        it("Should call insertAllTrafficRuleOption if securityGroupVPC is not None when adjustIPProtocolOptions is called", function() {
            spyOn(scope, 'insertAllTrafficRuleOption');
            scope.securityGroupVPC = 'blah';
            scope.adjustIPProtocolOptions(); 
            expect(scope.insertAllTrafficRuleOption).toHaveBeenCalled();
        });

        it("Should call insertCustomProtocolRuleOption if securityGroupVPC is not None when adjustIPProtocolOptions is called", function() {
            spyOn(scope, 'insertCustomProtocolRuleOption');
            scope.securityGroupVPC = 'blah';
            scope.adjustIPProtocolOptions(); 
            expect(scope.insertCustomProtocolRuleOption).toHaveBeenCalled();
        });

        it("Should not call insertAllTrafficRuleOption if securityGroupVPC is None when adjustIPProtocolOptions is called", function() {
            spyOn(scope, 'insertAllTrafficRuleOption');
            scope.securityGroupVPC = 'None';
            scope.adjustIPProtocolOptions(); 
            expect(scope.insertAllTrafficRuleOption).not.toHaveBeenCalled();
        });

        it("Should call insertCustomProtocolRuleOption if securityGroupVPC is None when adjustIPProtocolOptions is called", function() {
            spyOn(scope, 'insertCustomProtocolRuleOption');
            scope.securityGroupVPC = 'None';
            scope.adjustIPProtocolOptions(); 
            expect(scope.insertCustomProtocolRuleOption).not.toHaveBeenCalled();
        });

        it("Should set ip-protocol-select element's selectedIndex to -1 when adjustIPProtocolOptions is called", function() {
            scope.adjustIPProtocolOptions(); 
            expect($('#ip-protocol-select').prop('selectedIndex')).toEqual(-1);
        });
    });

    describe("Function removeAllTrafficRuleOption Test", function() {

        it("Should remove ip-protocol-select element's option if the value is -1 when removeAllTrafficRuleOption is called", function() {
            setFixtures('<select id="ip-protocol-select"><option></option><option value="-1">-1</option></select>');
            scope.removeAllTrafficRuleOption(); 
            expect($('#ip-protocol-select').find("option[value='-1']").length).toEqual(0);
        });
    });

    describe("Function removeCustomProtocolRuleOption Test", function() {

        it("Should remove ip-protocol-select element's option if the value is 'custom' when removeAllTrafficRuleOption is called", function() {
            setFixtures('<select id="ip-protocol-select"><option></option><option value="custom">custom</option></select>');
            scope.removeCustomProtocolRuleOption(); 
            expect($('#ip-protocol-select').find("option[value='custom']").length).toEqual(0);
        });
    });

    describe("Function insertAllTrafficRuleOption Test", function() {

        it("Should add the all-traffic rule option to ip-protocol-select element when insertAllTrafficRuleOption is called", function() {
            setFixtures('<select id="ip-protocol-select"><option></option></select><div id="all-traffic-option-text">all traffic</div>');
            expect($('#ip-protocol-select').find("option[value='-1']").length).toEqual(0);
            scope.insertAllTrafficRuleOption(); 
            expect($('#ip-protocol-select').find("option[value='-1']").length).toEqual(1);
        });
    });

    describe("Function insertCustomProtocolRuleOption Test", function() {

        it("Should add the custom protocol rule option to ip-protocol-select element when insertCustomProtocolRuleOption is called", function() {
            setFixtures('<select id="ip-protocol-select"><option></option></select><div id="custom-protocol-option-text">custom protocol</div>');
            expect($('#ip-protocol-select').find("option[value='custom']").length).toEqual(0);
            scope.insertCustomProtocolRuleOption(); 
            expect($('#ip-protocol-select').find("option[value='custom']").length).toEqual(1);
        });
    });

    describe("Function getCustomProtocolNumber Test", function() {

        it("Should return the matching protocol number when getCustomProtocolNumber is called", function() {
            scope.internetProtocols = ["HOPOPT", "ICMP", "IGMP"];
            var output = scope.getCustomProtocolNumber('igmp'); 
            expect(output).toEqual(2);
        });

        it("Should return '' if no matching protocol is found when getCustomProtocolNumber is called", function() {
            scope.internetProtocols = ["HOPOPT", "ICMP", "IGMP"];
            var output = scope.getCustomProtocolNumber('noProtocol'); 
            expect(output).toEqual('');
        });
    });

    describe("Function getCustomProtocolName Test", function() {

        it("Should return the matching protocol name when getCustomProtocolName is called", function() {
            scope.internetProtocols = ["HOPOPT", "ICMP", "IGMP"];
            var output = scope.getCustomProtocolName(2); 
            expect(output).toEqual('IGMP');
        });

        it("Should return the same, input protocol number if input is not a number when getCustomProtocolName is called", function() {
            scope.internetProtocols = ["HOPOPT", "ICMP", "IGMP"];
            var output = scope.getCustomProtocolName('notNumber'); 
            expect(output).toEqual('notNumber');
        });
    });

    describe("Function isCustomProtocol Test", function() {

        it("Should return true if the input is a number when isCustomProtocol is called", function() {
            var output = scope.isCustomProtocol(2); 
            expect(output).toBeTruthy();
        });

        it("Should return false if the input is '-1' when isCustomProtocol is called", function() {
            var output = scope.isCustomProtocol('-1'); 
            expect(output).not.toBeTruthy();
        });

        it("Should return false if the input is not a number when isCustomProtocol is called", function() {
            var output = scope.isCustomProtocol('igmp'); 
            expect(output).not.toBeTruthy();
        });
    });

    describe("Function verifyCustomProtocol Test", function() {

        it("Should return true if customProtocol is not a number and found in internetProtocols list when verifyCustomProtocol is called", function() {
            scope.internetProtocols = ["HOPOPT", "ICMP", "IGMP"];
            scope.customProtocol = 'igmp';
            var output = scope.verifyCustomProtocol(); 
            expect(output).toBeTruthy();
        });

        it("Should return false if customProtocol is not a number and not found in internetProtocols list when verifyCustomProtocol is called", function() {
            scope.internetProtocols = ["HOPOPT", "ICMP", "IGMP"];
            scope.customProtocol = 'notProtocol';
            var output = scope.verifyCustomProtocol(); 
            expect(output).not.toBeTruthy();
        });

        it("Should return true if customProtocol is a number and found in internetProtocols list when verifyCustomProtocol is called", function() {
            scope.internetProtocols = ["HOPOPT", "ICMP", "IGMP"];
            scope.customProtocol = 2;
            var output = scope.verifyCustomProtocol(); 
            expect(output).toBeTruthy();
        });

        it("Should return false if customProtocol is a number and not found in internetProtocols list when verifyCustomProtocol is called", function() {
            scope.internetProtocols = ["HOPOPT", "ICMP", "IGMP"];
            scope.customProtocol = 3;
            var output = scope.verifyCustomProtocol(); 
            expect(output).not.toBeTruthy();
        });
    });

    describe("Function scanForCustomProtocols Test", function() {

        beforeEach(function() {
            scope.initRules('{"rules_array": [{"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol":"tcp","from_port":"3389"}, {"to_port":"3389","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"10.5.1.66/32","name":null}],"ip_protocol": 2,"from_port":"3389"}],"rules_egress_array": [{"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol":"tcp","from_port":"22"}, {"to_port":"22","grants":[{"owner_id":null,"group_id":null,"cidr_ip":"0.0.0.0/0","name":null}],"ip_protocol": 1,"from_port":"22"}],"json_endpoint": "localhost/json", "protocols_json_endpoint": "localhost/api"}');
        });

        it("Should convert the custom protocol's number to name for rulesArray when scanForCustomProtocols is called", function() {
            scope.internetProtocols = ["HOPOPT", "ICMP", "IGMP"];
            expect(scope.rulesArray[1].ip_protocol).toEqual(2);
            expect(scope.rulesArray[1].custom_protocol).toEqual(undefined);
            scope.scanForCustomProtocols();
            expect(scope.rulesArray[1].custom_protocol).toEqual('IGMP');
        });

        it("Should convert the custom protocol's number to name for rulesEgressArray when scanForCustomProtocols is called", function() {
            scope.internetProtocols = ["HOPOPT", "ICMP", "IGMP"];
            expect(scope.rulesEgressArray[1].ip_protocol).toEqual(1);
            expect(scope.rulesEgressArray[1].custom_protocol).toEqual(undefined);
            scope.scanForCustomProtocols();
            expect(scope.rulesEgressArray[1].custom_protocol).toEqual('ICMP');
        });
    });
});
