/**
 * @fileOverview Scaling Group Create Policy page JS
 * @requires AngularJS
 *
 */

// Add Scaling Group Policy page includes the Create Alarm dialog, so pull in that module
angular.module('ScalingGroupPolicy', ['CreateAlarm', 'EucaConsoleUtils'])
    .controller('ScalingGroupPolicyCtrl', function ($rootScope, $scope, eucaNumbersOnly) {
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
            $scope.$watch('adjustmentAmount', function (newVal) {
                if(newVal) {
                    $scope.adjustmentAmount = eucaNumbersOnly(newVal);
                    $scope.isNotValid = false;
                } else {
                    $scope.isNotValid = true;
                }
                $scope.checkRequiredInput();
            });
            $scope.$watch('coolDown', function (newVal) {
                if(newVal) {
                    $scope.coolDown = eucaNumbersOnly(newVal);
                    $scope.isNotValid = false;
                } else {
                    $scope.isNotValid = true;
                }
                $scope.checkRequiredInput();
            });
            $scope.$watch('alarm', function () {
                $scope.checkRequiredInput();
            });

            $scope.$on('alarm_created', function ($event, promise) {
                promise.then(function success (result) {
                    // Add new alarm to choices and set it as selected
                    var newAlarm = result.data && result.data.new_alarm;
                    $rootScope.alarmChoices[newAlarm] = newAlarm;
                    $rootScope.alarm = newAlarm;
                    $scope.isCreatingAlarm = false;
                });
            });
        };
        $scope.setFocus = function () {
            $scope.policyForm.find('input#name').focus();
            $(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
                var modal = $(this);
                var inputElement = modal.find('input[type!=hidden]').get(0);
                var modalButton = modal.find('button').get(0);
                if (!!inputElement) {
                    inputElement.focus();
                } else if (!!modalButton) {
                    modalButton.focus();
                }
            });
            $(document).on('close.fndtn.reveal', '[data-reveal]', function () {
                document.getElementById('create-alarm-form').reset();
            });
            $(document).on('closed.fndtn.reveal', '[data-reveal]', function () {
                $('input#name').focus();
            });
        };
    })
;

