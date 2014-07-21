/**
 * @fileOverview Elastic IPs landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('ElasticIPsPage', ['LandingPage'])
    .config(function($locationProvider) {
        $locationProvider.html5Mode(true);
    })
    .controller('ElasticIPsCtrl', function ($scope, $location) {
        $scope.publicIP = '';
        $scope.instanceID = '';
        $scope.urlParams = $location.search();
        $scope.initChosenSelectors = function () {
            $('#instance_id').chosen({'width': '80%', 'search_contains': true});
        };
        $scope.initController = function () {
            $scope.initChosenSelectors();
            // Open allocate IP modal based on query string arg
            if ($scope.urlParams['allocate']) {
                $('#allocate-ip-modal').foundation('reveal', 'open');
            }
            $scope.setWatch();
        };
        $scope.setWatch = function () {
            $(document).on('close', '[data-reveal]', function () {
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
            $scope.instanceID = eip['instance_name'] || '';
            $scope.publicIP = eip['public_ip'];
            modal.foundation('reveal', 'open');
        };
    });

