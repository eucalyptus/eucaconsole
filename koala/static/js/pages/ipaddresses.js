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
        $scope.urlParams = $.url().param();
        $scope.displayType = $scope.urlParams['display'] || 'tableview';
        $scope.initChosenSelectors = function () {
            $('#instance_id').chosen({'width': '80%', 'search_contains': true});
        };
        $scope.initController = function () {
            $scope.initChosenSelectors();
        };
        $scope.revealModal = function (action, eip, instance_id) {
            instance_id = instance_id || '';
            var modal = $('#' + action + '-ip-modal');
            $scope.publicIP = eip;
            $scope.instanceID = instance_id;
            modal.foundation('reveal', 'open');
        };
    });

