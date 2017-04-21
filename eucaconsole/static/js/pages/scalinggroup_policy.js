/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview Scaling Group Create Policy page JS
 * @requires AngularJS
 *
 */

// Add Scaling Group Policy page includes the Create Alarm dialog, so pull in that module
angular.module('ScalingGroupPolicy', ['EucaConsoleUtils', 'CloudWatchCharts', 'CreateAlarmModal', 'ModalModule'])
    .controller('ScalingGroupPolicyCtrl', function ($rootScope, $scope, eucaNumbersOnly) {
        $scope.policyForm = $('#add-policy-form');
        $rootScope.alarmChoices = {};
        $rootScope.alarm = '';
        $scope.policyName = '';
        $scope.adjustmentAmount = 1;
        $scope.coolDown = 300;
        $scope.isNotValid = true;
        $scope.initController = function (alarmChoices) {
            $rootScope.alarmChoices = alarmChoices;
        };
        $scope.$on('alarmStateView:refreshList', function ($event, args) {
            // Add new alarm to choices and set it as selected
            var newAlarm = args.name;
            $rootScope.alarmChoices[newAlarm] = newAlarm;
            $rootScope.alarm = newAlarm;
            $scope.isCreatingAlarm = false;
        });
    })
;

