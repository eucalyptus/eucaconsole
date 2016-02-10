/**
 * @fileOverview Elastic IPs landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('ElasticIPsPage', ['LandingPage'])
    .controller('ElasticIPsCtrl', function ($scope) {
        $scope.publicIP = '';
        $scope.allocationID = '';
        $scope.instanceID = '';
        $scope.isNotValid = true;
        $scope.urlParams = $.url().param();
        $scope.multipleItemsSelected = false;
        $scope.initChosenSelectors = function () {
            $('#instance_id').chosen({'width': '80%', 'search_contains': true});
        };
        $scope.initController = function () {
            $scope.initChosenSelectors();
            // Open allocate IP modal based on query string arg
            $(document).ready(function () {
                if ($scope.urlParams.allocate) {
                    $('#allocate-ip-modal').foundation('reveal', 'open');
                }
            });
            $scope.setWatch();
        };
        $scope.setWatch = function () {
            $(document).on('open.fndtn.reveal', '[data-reveal]', function () {
                // Set the IP Count value to be 1 when re-opened
                var modal = $(this);
                modal.find('#ipcount').val('1');
            });
            $(document).on('close.fndtn.reveal', '[data-reveal]', function () {
                // Turn off the listeners on #ipcount
                $(document).off('input', '#ipcount');
                $(document).off('change', '#ipcount');
                // Reset the submit button to be disabled
                $scope.isNotValid = true;
                $scope.$apply();
            });
        };
        $scope.revealModal = function (action, eip) {
            var modal = $('#' + action + '-ip-modal');
            $scope.instanceID = eip.instance_name || '';
            $scope.publicIP = eip.public_ip;
            $scope.allocationID = eip.allocation_id;
            modal.foundation('reveal', 'open');
        };
        $scope.revealReleaseIPsModal = function (checkedItems) {
            var modal = $('#release-ip-modal');
            var checkedIPs = checkedItems.map(function (item) {
                return item.public_ip;
            });
            $scope.publicIP = checkedIPs.join(', ');
            $scope.multipleItemsSelected = checkedIPs.length > 1;
            modal.foundation('reveal', 'open');
        };
        $scope.revealDisassociateIPsModal = function (checkedItems) {
            var modal = $('#disassociate-ip-modal');
            var checkedIPs = [];
            var instanceIDs = [];
            checkedItems.forEach(function (item) {
                if (item.instance_id) {
                    checkedIPs.push(item.public_ip);
                    instanceIDs.push(item.instance_id);
                }
            });
            $scope.publicIP = checkedIPs.join(', ');
            $scope.instanceID = instanceIDs.join(', ');
            $scope.multipleItemsSelected = checkedIPs.length > 1;
            modal.foundation('reveal', 'open');
        };
    })
    .filter('attachedOnly', function() {
        return function (items) {
            return items.filter(function (item) {
                return !!item.instance_id;
            });
        };
    });

