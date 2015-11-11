/**
 * @fileOverview ELB Security Group Rules Warning JS
 * @requires AngularJS
 *
 */
angular.module('ELBSecurityGroupRulesWarning', [])
.service('eucaCheckELBSecurityGroupRules', function() {
    /**
     * Check security group rules to determine if inbound/outbound ports cover listener and health check ports
     */
    return function(scope) {
        var inboundChecksPass = true;
        var outboundChecksPass = true;
        var securityGroupInboundPorts = [];
        var securityGroupOutboundPorts = [];
        scope.selectedSecurityGroups = scope.securityGroupCollection.filter(function (group) {
            if (scope.securityGroups.indexOf(group.id) !== -1) {
                return group;
            }
        });
        // Collect inbound/outbound ports from security group rules
        scope.selectedSecurityGroups.forEach(function (sgroup) {
            // Collect Inbound ports
            sgroup.rules.forEach(function (rule) {
                if (rule.from_port) {
                    securityGroupInboundPorts.push(parseInt(rule.from_port, 10));
                }
                if (rule.to_port && rule.to_port !== rule.from_port) {
                    securityGroupInboundPorts.push(parseInt(rule.to_port, 10));
                }
                if (rule.ip_protocol === '-1' && securityGroupInboundPorts.indexOf(-1) === -1) {
                    securityGroupInboundPorts.push(-1);  // Add "all traffic" inbound rule
                }
            });
            // Outbound ports
            sgroup.rules_egress.forEach(function (rule) {
                if (rule.from_port) {
                    securityGroupOutboundPorts.push(parseInt(rule.from_port, 10));
                }
                if (rule.to_port && rule.to_port !== rule.from_port) {
                    securityGroupOutboundPorts.push(parseInt(rule.to_port, 10));
                }
                if (rule.ip_protocol === '-1' && securityGroupOutboundPorts.indexOf(-1) === -1) {
                    securityGroupOutboundPorts.push(-1);  // Add "all traffic" outbound rule
                }
            });
        });
        // Collect ports from configured listeners
        scope.listenerArray.forEach(function (listener) {
            if (scope.loadBalancerInboundPorts.indexOf(listener.fromPort) === -1) {
                scope.loadBalancerInboundPorts.push(listener.fromPort);
            }
            if (scope.loadBalancerOutboundPorts.indexOf(listener.toPort) === -1) {
                scope.loadBalancerOutboundPorts.push(listener.toPort);
            }
        });
        // Collect port from health check
        if (scope.pingPort && scope.loadBalancerOutboundPorts.indexOf(scope.pingPort) === -1) {
            scope.loadBalancerOutboundPorts.push(scope.pingPort);
        }
        // Compare listener and health check ports with selected security groups
        scope.loadBalancerInboundPorts.forEach(function (port) {
            if (securityGroupInboundPorts.indexOf(port) === -1) {
                inboundChecksPass = false;
            }
        });
        scope.loadBalancerOutboundPorts.forEach(function (port) {
            if (securityGroupOutboundPorts.indexOf(port) === -1) {
                outboundChecksPass = false;
            }
        });
        if (securityGroupInboundPorts.indexOf(-1) !== -1) {
            inboundChecksPass = true;  // Pass inbound check if "all traffic" rule
        }
        if (securityGroupOutboundPorts.indexOf(-1) !== -1) {
            outboundChecksPass = true;  // Pass outbound check if "all traffic" rule
        }
        return inboundChecksPass && outboundChecksPass;
    };
});

