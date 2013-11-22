/**
 * @fileOverview Security Group rules editor JS
 * @requires AngularJS
 *
 */

angular.module('SecurityGroupRules', [])
    .controller('SecurityGroupRulesCtrl', function ($scope) {
        $scope.rulesEditor = $('#rules-editor');
        $scope.rulesTextarea = $scope.rulesEditor.find('textarea#rules');
        $scope.rulesArray = [];
        $scope.resetValues = function () {
            $scope.trafficType = 'ip';
            $scope.fromPort = '';
            $scope.toPort = '';
            $scope.cidrIp = '';
            $scope.selectedProtocol = '';
            $scope.ipRequired = false;
            $scope.icmpRange = '-1';  // Default to 'All' if ICMP traffic type
            $scope.groupName = '';
            $('.ip-protocol').chosen({'width': '90%'});
            $scope.setIpRequired();
        };
        $scope.setIpRequired = function () {
            if ($scope.selectedProtocol && $scope.trafficType == 'ip') {
                $scope.ipRequired = true;
            }
        };
        $scope.resetValues();
        $scope.syncRules = function () {
            $scope.rulesTextarea.val(JSON.stringify($scope.rulesArray));
            $scope.resetValues();
        };
        $scope.initRules = function (rulesArray) {
            // Get existing rules and shove into scope
            $scope.rulesArray = JSON.parse(rulesArray);
            $scope.syncRules();
        };
        $scope.removeRule = function (index, $event) {
            $event.preventDefault();
            $scope.rulesArray.splice(index, 1);
            $scope.syncRules();
        };
        $scope.addRule = function ($event) {
            $event.preventDefault();
            // Trigger form validation to prevent borked rule entry
            $($event.currentTarget).closest('form').trigger('validate');
            // Add the rule
            $scope.rulesArray.push({
                'from_port': $scope.fromPort,
                'to_port': $scope.toPort,
                'ip_protocol': $scope.selectedProtocol == 'icmp' ? 'icmp' : 'tcp',
                'grants': [{
                    'cidr_ip': $scope.cidrIp ? $scope.cidrIp : null,
                    'group_id': null,
                    'name': $scope.groupName ? $scope.groupName : null
                }],
                'fresh': 'new'
            });
            $scope.syncRules();
        };
        $scope.setPorts = function (port) {
            if (!isNaN(port)) {
                $scope.fromPort = port;
                $scope.toPort = port;
            } else {
                $scope.fromPort = $scope.toPort = '';
            }
            $('.groupname').chosen({'width': '50%'});
        };
        $scope.refreshIPAddressValidation = function () {
            $('.ipaddress').removeClass('error');
        }
    });
;


// Avoid clobbering the tag editor, since we have multiple ng-app="" attributes on the page.
angular.element(document).ready(function() {
    angular.bootstrap(document.getElementById('tag-editor'), ['TagEditor']);
});

