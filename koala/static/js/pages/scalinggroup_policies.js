/**
 * @fileOverview Scaling Group Policies page JS
 * @requires AngularJS
 *
 */

angular.module('ScalingGroupPolicies', [])
    .controller('ScalingGroupPoliciesCtrl', function ($scope) {
        $scope.policyName = '';
        $scope.deleteModal = $('#delete-policy-modal');
        $scope.revealDeleteModal = function (policyName) {
            var modal = $scope.deleteModal;
            $scope.policyName = policyName;
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

