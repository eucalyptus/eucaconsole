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
            $scope.policyName = policyName;
            $scope.deleteModal.foundation('reveal', 'open');
        };
    })
;

