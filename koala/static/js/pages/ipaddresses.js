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
        $scope.initChosenSelectors = function () {
            $('#instance_id').chosen({'width': '80%', 'search_contains': true});
        };
        $scope.initController = function () {
            $scope.initChosenSelectors();
        };
        $scope.revealModal = function (action, eip) {
            var modal = $('#' + action + '-ip-modal');
            $scope.instanceID = eip['instance_name'] || '';
            $scope.publicIP = eip['public_ip'];
            modal.foundation('reveal', 'open');
            setTimeout(function(){ 
                    var inputElement = modal.find('input[type!=hidden]').get(0); 
                    if( inputElement != undefined ){ 
                        inputElement.focus() 
                    }else{ 
                        modal.find('button').get(0).focus(); 
                    } 
               }, 1000); 
        };
    });

