/**
 * @fileOverview Snapshots landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('SecurityGroupsPage', ['LandingPage'])
    .controller('SecurityGroupsCtrl', function ($scope) {
        $scope.securitygroupID = '';
        $scope.revealModal = function (action, securitygroup) {
            var modal = $('#' + action + '-securitygroup-modal');
            $scope.securitygroupID = securitygroup['id'];
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
    })
;
