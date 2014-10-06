/**
 * @fileOverview Security Group rules editor JS
 * @requires AngularJS
 *
 */

angular.module('SecurityGroupRules', [])
    .controller('SecurityGroupRulesCtrl', function ($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.rulesEditor = $('#rules-editor');
        $scope.rulesTextarea = $scope.rulesEditor.find('textarea#rules');
        $scope.rulesEgressTextarea = $scope.rulesEditor.find('textarea#rules_egress');
        $scope.rulesArray = [];
        $scope.rulesEgressArray = [];
        $scope.jsonEndpoint='';
        $scope.securityGroupList = [];
        $scope.securityGroupVPC = '';
        $scope.selectedProtocol = '';
        $scope.isRuleNotComplete = true;
        $scope.inboundButtonClass = 'active';
        $scope.outboundButtonClass = 'inactive';
        $scope.trafficType = '';
        $scope.ruleType = 'inbound';
        $scope.resetValues = function () {
            $scope.trafficType = 'ip';
            $scope.fromPort = '';
            $scope.toPort = '';
            $scope.cidrIp = '';
            $scope.selectedProtocol = '';
            $scope.icmpRange = '-1';  // Default to 'All' if ICMP traffic type
            $scope.groupName = '';
            $scope.ipProtocol = 'tcp';
            $scope.hasDuplicatedRule = false;
            $scope.hasInvalidOwner = false;
            $('#ip-protocol-select').chosen({'width': '90%', search_contains: true});
            $('#ip-protocol-select').prop('selectedIndex', -1);
            $('#ip-protocol-select').trigger('chosen:updated');
            $scope.cleanupSelections();
            $scope.adjustIPProtocolOptions();
        };
        $scope.syncRules = function () {
            $scope.rulesTextarea.val(JSON.stringify($scope.rulesArray));
            $scope.rulesEgressTextarea.val(JSON.stringify($scope.rulesEgressArray));
            $scope.resetValues();
        };
        $scope.initRules = function (rulesJson, rulesEgressJson, jsonEndpoint) {
            rulesJson = rulesJson.replace(/__apos__/g, "\'").replace(/__dquote__/g, '\\"').replace(/__bslash__/g, "\\");
            $scope.rulesArray = JSON.parse(rulesJson);
            $scope.rulesEgressArray = JSON.parse(rulesEgressJson);
            $scope.jsonEndpoint=jsonEndpoint;
            $scope.syncRules();
            $scope.setWatchers();
        };
        $scope.clearRules = function () {
            $scope.rulesArray = [];
            $scope.rulesEgressArray = [];
            $scope.syncRules();
        };
        $scope.getAllSecurityGroups = function (vpc) {
            var csrf_token = $('#csrf_token').val();
            var data = "csrf_token=" + csrf_token + "&vpc_id=" + vpc;
            $http({method:'POST', url:$scope.jsonEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.securityGroupList = results;
            });
        };
        $scope.cleanupSelections = function () {
            $timeout( function(){
                if( $('#ip-protocol-select').children('option').first().html() == '' ){
                    $('#ip-protocol-select').children('option').first().remove();
                } 
                if( $('#groupname-select').children('option').first().html() == '' ){
                    $('#groupname-select').children('option').first().remove();
                }
            }, 500);
        };
        $scope.checkRequiredInput = function () {
            // By default, the Add Rule button is enabled when entering the check
            $scope.isRuleNotComplete = false;
            // If any of the required input fields are mising, disable the Add Rule button
            if( $scope.hasDuplicatedRule == true ){
                $scope.isRuleNotComplete = true;
            }
            if( $scope.selectedProtocol !== 'icmp' && $scope.selectedProtocol !== '-1' ){
                if( $scope.fromPort === '' || $scope.fromPort === undefined ){
                    $scope.isRuleNotComplete = true;
                }else if( $scope.toPort === '' || $scope.toPort === undefined ){
                    $scope.isRuleNotComplete = true;
                }
            }
            if( $scope.trafficType === 'ip' ){
                if( $scope.cidrIp === '' || $scope.cidrIp === undefined ){
                    $scope.isRuleNotComplete = true;
                }
            }else if( $scope.trafficType === 'securitygroup' ){
                if( $scope.groupName === '' || $scope.groupName === undefined ){
                    $scope.isRuleNotComplete = true;
                }
            }
        };
        // Watch for those two attributes update to trigger the duplicated rule check in real time
        $scope.setWatchers = function () {
            $scope.$watch('selectedProtocol', function(){ 
                $scope.checkRequiredInput();
                // Set the defalt CIDR IP value to be "Open to all addresses"
                // In case of choosing "All traffic" Protocol
                if ($scope.selectedProtocol == '-1') {
                    $scope.cidrIp = '0.0.0.0/0';
                } else {
                    $scope.cidrIp = '';
                }
            });
            $scope.$watch('fromPort', function(){ 
                $scope.checkRequiredInput();
            });
            $scope.$watch('toPort', function(){ 
                $scope.checkRequiredInput();
            });
            $scope.$watch('icmpRange', function(){ 
                $scope.checkRequiredInput();
            });
            $scope.$watch('cidrIp', function(){ 
                $scope.checkForDuplicatedRules();
                $scope.checkRequiredInput();
            });
            $scope.$watch('groupName', function(){
                if( $scope.groupName !== '' ){
                    $scope.trafficType = 'securitygroup';
                }
                $scope.hasInvalidOwner = false;
                $scope.checkForDuplicatedRules();
                $scope.checkRequiredInput();
            });
            $scope.$watch('trafficType', function(){ 
                $scope.checkForDuplicatedRules();
                $scope.checkRequiredInput();
            });
            $scope.$watch('securityGroupVPC', function() {
                $scope.getAllSecurityGroups($scope.securityGroupVPC);
            });
            $scope.$watch('securityGroupList', function() {
                if ($scope.securityGroupList.length) {
                    $scope.checkRulesForDeletedSecurityGroups();
                }
            }, true);
            $scope.$on('updateVPC', function($event, vpc) {
                if (vpc === undefined || $scope.securityGroupVPC == vpc) {
                    return;
                }
                $scope.securityGroupVPC = vpc;
                // In 'Create new security group' mode,
                if ($('select#vpc_network').length > 0) {
                    // Clear previously selected rules when VPC is changed
                    $scope.clearRules();
                    // Add the default outbound rule for VPC security group
                    if ($scope.securityGroupVPC != '') {
                        $scope.addDefaultOutboundRule();
                    } 
                }
                // When NoVPC is selected, which the tab to 'inbound'
                if ($scope.securityGroupVPC == '') {
                    $scope.selectRuleType('inbound'); 
                }
                // For VPC, include the option '-1' for ALL IP Protocols
                $scope.adjustIPProtocolOptions();
            });
            $(document).on('keyup', '#input-cidr-ip', function () {
                $scope.$apply(function() {
                    $scope.trafficType = 'ip';
                });
            });
            $(document).on('click', '#sgroup-use-my-ip', function () {
                $scope.$apply(function() {
                    $scope.trafficType = 'ip';
                });
            });
            $(document).on('closed', '#create-securitygroup-modal', function () {
                $scope.$apply(function(){
                    $scope.rulesArray = [];  // Empty out the rules when the dialog is closed 
                    $scope.rulesEgressArray = [];  // Empty out the rules when the dialog is closed 
                    $scope.syncRules();
                });
            });
        };
        // In case of the duplicated rule, add the class 'disabled' to the submit button
        $scope.getAddRuleButtonClass = function () {
            if( $scope.hasDuplicatedRule == true ){
                return 'disabled';
            }
        };
        // Run through the existing rules to verify that
        // the security groups in the rules are still valid
        $scope.checkRulesForDeletedSecurityGroups = function () {
            var invalidRulesArray = [];
            var invalidRulesEgressArray = [];
            // Check the ingress rules
            angular.forEach($scope.rulesArray, function (rule) {
                if (rule.grants[0].group_id != null) {
                    var exists = false;
                    angular.forEach($scope.securityGroupList, function (sg) {
                        if (sg.id == rule.grants[0].group_id) {
                            exists = true;
                        } 
                    });
                    if (!exists) {
                        invalidRulesArray.push(rule); 
                    }
                }
            });
            // Check the egress rules
            angular.forEach($scope.rulesEgressArray, function (rule) {
                if (rule.grants[0].group_id != null) {
                    var exists = false;
                    angular.forEach($scope.securityGroupList, function (sg) {
                        if (sg.id == rule.grants[0].group_id) {
                            exists = true;
                        } 
                    });
                    if (!exists) {
                        invalidRulesEgressArray.push(rule); 
                    }
                }
            });
            // Emit the signal to trigger invalid rules warning
            if (invalidRulesArray.length > 0 || invalidRulesEgressArray.length > 0) {
                $scope.$emit('invalidRulesWarning', invalidRulesArray, invalidRulesEgressArray);
            }
        };
        // Run through the existing rules with the newly create rule
        // to ensure that the new rule does not exist already
        $scope.checkForDuplicatedRules = function () {
            $scope.hasDuplicatedRule = false;
            // Create a new array block based on the current user input on the panel
            var thisRuleArrayBlock = $scope.createRuleArrayBlock();
            var compareArray = [];
            if ($scope.ruleType == 'inbound') {
                compareArray = $scope.rulesArray;
            } else {
                compareArray = $scope.rulesEgressArray;
            }
            for( var i=0; i < compareArray.length; i++){
                // Compare the new array block with the existing ones
                if( $scope.compareRules(thisRuleArrayBlock, compareArray[i]) ){
                    // Detected that the new rule is a dup
                    // this value will disable the "Add Rule" button to prevent the user from submitting
                    $scope.hasDuplicatedRule = true;
                    return;
                }
            }
            return;
        };
        // Compare the rules to determine if they are the same rules
        // First, compare the three common attributes [from_port, to_port, ip_protocol]
        // Second, the rule can have a direct IP range value or have an access granted group name
        // Third, if the rule has the direct IP range value, compare that value and return true if they are same, else return false
        //        if the rule has the granted gropu, compare that value instead. 
        $scope.compareRules = function(block1, block2){
            // IF the ports and the protocol are the same,
            if( block1.from_port == block2.from_port
                && block1.to_port == block2.to_port
                && block1.ip_protocol == block2.ip_protocol){
                // IF cidr_ip is not null, then compare cidr_ip  
                if( $scope.trafficType == "ip" && block1.grants[0].cidr_ip != null ){
                    if( block1.grants[0].cidr_ip == block2.grants[0].cidr_ip ){
                        // The rules are the same 
                        return true;
                    }else{
                        // the rules have different IP ranges
                        return false;
                    }
                // ELSE IF compare the group name
                }else if( block1.grants[0].name != null ){
                    if( block1.grants[0].name == block2.grants[0].name ){
                        // the rules are the same
                        return true;
                    }else{
                        // the rules have different granted group names
                        return false;
                    }
                }
            }
            // the rules have different ports or ip_protocol, or incomplete.
            return false;
        };
        $scope.removeRule = function (index, $event) {
            $event.preventDefault();
            if ($scope.ruleType == 'inbound') {
                $scope.rulesArray.splice(index, 1);
            } else {
                $scope.rulesEgressArray.splice(index, 1);
            }
            $scope.syncRules();
            $scope.$emit('securityGroupUpdate');
        };
        // Adjust the IP Protocol atrributes for specical cases
        $scope.adjustIpProtocol = function () {
            if ($scope.selectedProtocol === 'icmp') {
                $scope.fromPort = $scope.icmpRange;
                $scope.toPort = $scope.icmpRange;
                $scope.ipProtocol = 'icmp'
            } else if ($scope.selectedProtocol === 'udp') {
                $scope.ipProtocol = 'udp'
            } else if ($scope.selectedProtocol === '-1') {
                $scope.ipProtocol = '-1'
                $scope.fromPort = null;
                $scope.toPort = null;
            } else {
                $scope.ipProtocol = 'tcp'
            }
        };
        // Create an array block that represents a new security group rule submiitted by user
        $scope.createRuleArrayBlock = function () {
            var name = $scope.groupName ? $scope.trafficType == 'securitygroup' && $scope.groupName : null;
            var owner_id = null;
            var group_id = null;
            if (name !== null) {
                var idx = name.indexOf('/');
                if (idx > 0) {
                    owner_id = name.substring(0, idx);
                    name = name.substring(idx+1);
                }
                group_id=$scope.getGroupIdByName(name);
            }
            $scope.adjustIpProtocol();
            return {
                'from_port': $scope.fromPort,
                'to_port': $scope.toPort,
                // Warning: Ugly hack to properly set ip_protocol when 'udp' or 'icmp'
                'ip_protocol': $scope.ipProtocol,
                'grants': [{
                    'cidr_ip': $scope.cidrIp ? $scope.trafficType == 'ip' && $scope.cidrIp : null,
                    'group_id': group_id,
                    'name': name,
                    'owner_id': owner_id
                }],
                'rule_type': $scope.ruleType,
                'fresh': 'new'
            }; 
        };
        $scope.addRule = function ($event) {
            $event.preventDefault();
            if( $scope.hasDuplicatedRule == true || $scope.hasInvalidOwner == true ){
                return false;
            }
            // Trigger form validation to prevent borked rule entry
            var form = $($event.currentTarget).closest('form');
            form.trigger('validate');
            if (form.find('[data-invalid]').length) {
                return false;
            }
            // Add the rule
            if ($scope.ruleType == 'inbound') {
                $scope.rulesArray.push($scope.createRuleArrayBlock());
            } else {
                $scope.rulesEgressArray.push($scope.createRuleArrayBlock());
            }
            $scope.syncRules();
            $scope.$emit('securityGroupUpdate');
        };
        $scope.cancelRule = function ($event) {
            $event.preventDefault();
            $scope.resetValues();
        };
        $scope.setPorts = function (port) {
            if (!isNaN(parseInt(port, 10))) {
                $scope.fromPort = port;
                $scope.toPort = port;
            } else {
                $scope.fromPort = $scope.toPort = '';
            }
            $('#groupname-select').chosen({'width': '50%', search_contains: true, create_option: function(term){
                    $scope.hasInvalidOwner = false;
                    var chosen = this;
                    // validate the entry
                    var name = term;
                    var owner_id = null;
                    if (name !== null) {
                        var idx = name.indexOf('/');
                        if (idx > 0) {
                            owner_id = name.substring(0, idx);
                            name = name.substring(idx+1);
                        }
                    }
                    $timeout(function() {
                        if (owner_id !== null && (owner_id.length != 12 || isNaN(parseInt(owner_id, 10)))) {
                            $scope.hasInvalidOwner = true;
                            return;
                        }
                        chosen.append_option({
                            value: term,
                            text: term
                        });
                    });
                },
                create_option_text: 'Add Group',
            });
            $('#groupname-select').prop('selectedIndex', -1);
            $('#groupname-select').trigger('chosen:updated');
            $scope.cleanupSelections();
        };
        $scope.getGroupIdByName = function (name) {
            for( var i=0; i < $scope.securityGroupList.length; i++){
                if ($scope.securityGroupList[i]['name'] === name) {
                    return $scope.securityGroupList[i]['id'];
                }
            } 
            return null;
        };
        $scope.openToAllAddresses = function () {
            $scope.cidrIp = "0.0.0.0/0";
            $('#input-cidr-ip').focus();
        };
        $scope.useMyIP = function (myip) {
            $scope.cidrIp = myip + "/32";
            $('#input-cidr-ip').focus();
        };
        // Set the default outbound rule to open to all addresses -- Default action by AWS
        $scope.addDefaultOutboundRule = function () {
            var storeRuleType = $scope.ruleType; // Save the current ruleType value
            $scope.ruleType = 'outbound';   // Needs to set 'outbound' for the rule comparison
            $scope.ipProtocol = "-1";
            $scope.trafficType == "ip" 
            $scope.cidrIp = "0.0.0.0/0";
            $scope.fromPort = null;
            $scope.toPort = null;
            $scope.checkForDuplicatedRules();
            if ($scope.hasDuplicatedRule) {
                $scope.resetValues();
            } else {
                $scope.rulesEgressArray.push($scope.createRuleArrayBlock());
                $scope.syncRules();
            }
            $scope.ruleType = storeRuleType;   // Restore the ruleType value
        };
        $scope.selectRuleType = function (ruleType) {
            $scope.ruleType = ruleType;
            if ($scope.ruleType === 'inbound') {
                $scope.inboundButtonClass = 'active';
                $scope.outboundButtonClass = 'inactive';
            } else {
                $scope.inboundButtonClass = 'inactive';
                $scope.outboundButtonClass = 'active';
            }
        };
        $scope.adjustIPProtocolOptions = function () {
            $scope.removeAllTrafficRuleOption();
            if ($scope.securityGroupVPC != '') {
                // Allow All Traffic option to be selectable for VPC
                $scope.insertAllTrafficRuleOption();
            }
            $('#ip-protocol-select').prop('selectedIndex', -1);
            $('#ip-protocol-select').trigger('chosen:updated');
        };
        // Remove All Traffic rule, "-1 ()" from the option
        $scope.removeAllTrafficRuleOption  = function () {
            $('#ip-protocol-select').find("option[value='-1']").remove();
        };
        // Allow All Traffic, "-1", to be selectable for VPC
        $scope.insertAllTrafficRuleOption  = function () {
            var key = "-1";
            var value = $('#all-traffic-option-text').text();
            $('#ip-protocol-select').prepend($("<option></option>").attr("value", key).text(value));  
        };
    })
;
