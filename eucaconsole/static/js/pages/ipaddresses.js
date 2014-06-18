/**
 * @fileOverview Elastic IPs landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('ElasticIPsPage', ['LandingPage'])
    .controller('ElasticIPsCtrl', function ($scope) {
        $scope.publicIP = '';
        $scope.instanceID = '';
        $scope.isNotValid = true;
        $scope.urlParams = $.url().param();
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
            $(document).on('opened', '[data-reveal]', function () {
                $(document).on('input', '#ipcount', function () {
                    if( $scope.isNotValid === true ){
                        $scope.isNotValid = false;
                        $scope.$apply();
                    }
                });
                // For FireFox Selenium Test, which triggers "change" event when type input on the number inputbox.
                $(document).on('change', '#ipcount', function () {
                    if( $scope.isNotValid === true ){
                        $scope.isNotValid = false;
                        $scope.$apply();
                    }
                });
            });
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

