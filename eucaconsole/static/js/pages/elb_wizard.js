/**
 * @fileOverview Elastic Load Balancer Wizard JS
 * @requires AngularJS
 *
 */

wizardApp.controller('ELBWizardCtrl', function ($scope, $http, $timeout, eucaHandleError, eucaUnescapeJson) {
        $scope.elbForm = undefined;
        $scope.urlParams = undefined;
        $scope.isNotValid = true;
        $scope.elbName = '';
        $scope.vpcNetwork = '';
        $scope.vpcSubnet = '';
        $scope.vpcSubnetChoices = [];
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.setInitialValues(options);
            $scope.setWatcher();
            $scope.setFocus();
        };
        $scope.setInitialValues = function (options) {
            $scope.elbForm = $('#elb-form');
            $scope.urlParams = $.url().param();
            $scope.isNotValid = true;
        };
        $scope.setWatcher = function (){
            // Handle the next step tab click event
            $scope.$on('eventClickVisitNextStep', function($event, nextStep) {
                $scope.checkRequiredInput(nextStep);
                // Signal the parent wizard controller about the completion of the next step click event
                $scope.$emit('eventProcessVisitNextStep', nextStep);
            });
            $scope.$watch('elbName', function(){
               $scope.checkRequiredInput(1);
            });
        };
        $scope.setFocus = function () {
        };
        $scope.checkRequiredInput = function (step) {
            $scope.isNotValid = false;
            if (step === 1) {
                if ($scope.elbName === '') {
                    $scope.isNotValid = true;
                }
            }
            // Signal the parent wizard controller about the update of the validation error status
            $scope.$emit('updateValidationErrorStatus', $scope.isNotValid);
        };
        $scope.createELB = function () {
        };
    })
;

