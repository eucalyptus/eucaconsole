/**
 * @fileOverview Scaling Group Policies page JS
 * @requires AngularJS
 *
 */

angular.module('ScalingGroupPolicies', [])
    .controller('ScalingGroupPoliciesCtrl', function ($scope) {
        $scope.policyName = '';
        $scope.deleteModal = $('#delete-policy-modal');
        $scope.initPage = function () {
            $scope.setFocus();
            $scope.setDropdownMenusListener();
        };
        $scope.revealDeleteModal = function (policyName) {
            var modal = $scope.deleteModal;
            $scope.policyName = policyName;
            modal.foundation('reveal', 'open');
        };
        $scope.setFocus = function () {
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var inputElement = modal.find('input[type!=hidden]').get(0);
                var modalButton = modal.find('button').get(0);
                if (!!inputElement) {
                    inputElement.focus();
                } else if (!!modalButton) {
                    modalButton.focus();
                }
            });
        };
        $scope.setDropdownMenusListener = function () {
            var modals = $('[data-reveal]');
            modals.on('open', function () {
                $('.gridwrapper').find('.f-dropdown').filter('.open').css('display', 'none');
            });
            modals.on('close', function () {
                $('.gridwrapper').find('.f-dropdown').filter('.open').css('display', 'block');
            })
        };
    })
;

