/**
 * @fileOverview Scaling Group Create Policy page JS
 * @requires AngularJS
 *
 */

// Add Scaling Group Policy page includes the Create Alarm dialog, so pull in that module
angular.module('ScalingGroupPolicy', ['CreateAlarm'])
    .controller('ScalingGroupPolicyCtrl', function ($rootScope, $scope) {
        $scope.alarmModal = $('#create-alarm-modal');
        $scope.policyForm = $('#add-policy-form');
        $rootScope.alarmChoices = {};
        $rootScope.alarm = '';
        $scope.policyName = '';
        $scope.adjustmentAmount = 1;
        $scope.coolDown = 300;
        $scope.isNotValid = true;
        $scope.initController = function (alarmChoices) {
            $rootScope.alarmChoices = alarmChoices;
            $scope.setWatch();
            $scope.setFocus();
        };
        $scope.revealAlarmModal = function () {
            var modal = $scope.alarmModal;
            modal.foundation('reveal', 'open');
        };
        $scope.checkRequiredInput = function () { 
            $scope.isNotValid = false;
            if( $scope.policyName === '' || $scope.policyName === undefined ){
                $scope.isNotValid = true;
            }else if( $scope.adjustmentAmount === '' || $scope.adjustmentAmount === undefined ){
                $scope.isNotValid = true;
            }else if( $scope.coolDown === '' || $scope.coolDown === undefined ){
                $scope.isNotValid = true;
            }else if( $rootScope.alarm === '' || $rootScope.alarm === undefined || 
                $rootScope.alarm === null || $rootScope.alarm === '""' ){
                $scope.isNotValid = true;
            }
        };
        $scope.setWatch = function () {
            $scope.$watch('policyName', function () {
                $scope.checkRequiredInput();
            });
            $scope.$watch('adjustmentAmount', function () {
                $scope.checkRequiredInput();
            });
            $scope.$watch('coolDown', function () {
                $scope.checkRequiredInput();
            });
            $scope.$watch('alarm', function () {
                $scope.checkRequiredInput();
            });
        };
        $scope.setFocus = function () {
            $scope.policyForm.find('input#name').focus();
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
            $(document).on('close', '[data-reveal]', function () {
                var modal = $(this);
                modal.find('input[type="text"]').val('');
                modal.find('textarea').val('');
                modal.find('div.error').removeClass('error');
                modal.find('select').find('option').removeAttr("selected");
                modal.find('#threshold').val('');
                modal.find('#evaluation_periods').val(1);
                modal.find('#period').val(5);
            });
            $(document).on('closed', '[data-reveal]', function () {
                $('input#name').focus();
            });
        };
    })
;

