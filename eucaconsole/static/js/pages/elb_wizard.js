/**
 * @fileOverview Elastic Load Balancer Wizard JS
 * @requires AngularJS
 *
 */

wizardApp.controller('ELBWizardCtrl', function ($scope, $http, $timeout, eucaHandleError, eucaUnescapeJson) {
        $scope.elbForm = undefined;
        $scope.urlParams = undefined;
        $scope.elbName = '';
        $scope.isNotValid = true;
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.setInitialValues();
            $scope.setWatcher();
            $scope.setFocus();
        };
        $scope.setInitialValues = function () {
            $scope.elbForm = $('#elb-form');
            $scope.urlParams = $.url().param();
        };
        $scope.setWatcher = function (){
            $scope.$watch('elbName', function(){
                $scope.checkRequiredInput(1);
            });
            $scope.$on('eventClickVisitNextStep', function($event, nextStep) {
                $scope.checkRequiredInput(nextStep);
                $scope.$emit('eventProcessVisitNextStep', nextStep);
            });
        };
        $scope.setFocus = function () {
        };
        $scope.checkRequiredInput = function (step) {
            $scope.isNotValid = false;
            $scope.$emit('updateValidationErrorStatus', $scope.isNotValid);
        };
        $scope.createELB = function() {
        };
    })
;

