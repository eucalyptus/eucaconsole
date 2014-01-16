/**
 * @fileOverview Scaling Group Policies page JS
 * @requires AngularJS
 *
 */

angular.module('ScalingGroupPolicies', [])
    .controller('ScalingGroupPoliciesCtrl', function ($scope) {
        $scope.policyName = '';
        $scope.createModal = $('#create-policy-modal');
        $scope.deleteModal = $('#delete-policy-modal');
        $scope.alarmModal = $('#create-alarm-modal');
        $scope.revealCreateModal = function () {
            $scope.createModal.foundation('reveal', 'open');
            $('#alarm').chosen({'width': '80%'});
        };
        $scope.revealDeleteModal = function (policyName) {
            $scope.policyName = policyName;
            $scope.deleteModal.foundation('reveal', 'open');
        };
        $scope.revealAlarmModal = function () {
            $scope.createModal.foundation('reveal', 'open');
            $scope.alarmModal.foundation('reveal', 'open');
        };
    })
;

