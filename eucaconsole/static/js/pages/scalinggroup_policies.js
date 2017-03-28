/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Scaling Group Policies page JS
 * @requires AngularJS
 *
 */

angular.module('ScalingGroupPolicies', ['CustomFilters'])
    .controller('ScalingGroupPoliciesCtrl', function ($scope) {
        $scope.policyName = '';
        $scope.deleteModal = $('#delete-policy-modal');
        $scope.initPage = function () {
            $scope.setFocus();
        };
        $scope.revealDeleteModal = function (policyName) {
            var modal = $scope.deleteModal;
            $scope.policyName = policyName;
            modal.foundation('reveal', 'open');
        };
        $scope.setFocus = function () {
            $(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
                var modal = $(this);
                var inputElement = modal.find('input[type!=hidden]').get(0);
                if (!!inputElement) {
                    inputElement.focus();
                }
            });
        };
    })
;

