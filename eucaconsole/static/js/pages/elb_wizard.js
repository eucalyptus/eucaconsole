/**
 * @fileOverview Elastic Load Balancer Wizard JS
 * @requires AngularJS
 *
 */

angular.module('ELBWizard', ['EucaConsoleUtils'])
    .controller('ELBWizardCtrl', function ($scope, $http, $timeout, eucaHandleError, eucaUnescapeJson) {
        $scope.elbName = '';
        $scope.urlParams = undefined;
        $scope.summarySection = undefined;
        $scope.currentStepIndex = 1;
        $scope.step1Invalid = true;
        $scope.step2Invalid = true;
        $scope.step3Invalid = true;
        $scope.isNotValid = true;
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.setInitialValues();
            $scope.setWatcher();
            $scope.setFocus();
        };
        $scope.setInitialValues = function () {
            $scope.urlParams = $.url().param();
            $scope.summarySection = $('.summary');
            $scope.currentStepIndex = 1;
        };
        $scope.checkRequiredInput = function () {
            $scope.isNotValid = false;
        };
        $scope.setWatcher = function (){
            $scope.$watch('currentStepIndex', function(){
                 if( $scope.currentStepIndex != 1 ){
                     $scope.setWizardFocus($scope.currentStepIndex);
                 }
                $scope.checkRequiredInput();
            });
            $scope.$watch('elbName', function(){
                $scope.checkRequiredInput();
            });
            $(document).on('open', '[data-reveal]', function () {
                // When a dialog opens, reset the progress button status
                $(this).find('.dialog-submit-button').css('display', 'block');                
                $(this).find('.dialog-progress-display').css('display', 'none');                
                // Broadcast initModal signal to trigger the modal initialization
                $scope.$broadcast('initModal');
            });
            $(document).on('opened', '[data-reveal]', function () {
            });
            $(document).on('submit', '[data-reveal] form', function () {
                // When a dialog is submitted, display the progress button status
                $(this).find('.dialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
            });
            $(document).on('close', '[data-reveal]', function () {
                var modal = $(this);
                modal.find('input[type="text"]').val('');
                modal.find('input[type="number"]').val('');
                modal.find('input:checked').attr('checked', false);
                modal.find('textarea').val('');
                modal.find('div.error').removeClass('error');
                var chosenSelect = modal.find('select');
                if (chosenSelect.length > 0 && chosenSelect.attr('multiple') === undefined) {
                    chosenSelect.prop('selectedIndex', 0);
                    chosenSelect.trigger("chosen:updated");
                }
            });
        };
        $scope.setFocus = function () {
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var modalID = $(this).attr('id');
                if( modalID.match(/terminate/)  || modalID.match(/delete/) || modalID.match(/release/) ){
                    var closeMark = modal.find('.close-reveal-modal');
                    if(!!closeMark){
                        closeMark.focus();
                    }
                }else{
                    var inputElement = modal.find('input[type!=hidden]').get(0);
                    var modalButton = modal.find('button').get(0);
                    if (!!inputElement && inputElement.value === '') {
                        inputElement.focus();
                    } else if (!!modalButton) {
                        modalButton.focus();
                    }
               }
            });
        };
        $scope.setWizardFocus = function (stepIdx) {
            var tabElement = $(document).find('#tabStep'+stepIdx).get(0);
            if (!!tabElement) {
                tabElement.focus();
            }
        };
        $scope.visitNextStep = function (nextStep, $event) {
            // Trigger form validation before proceeding to next step
            //$scope.launchForm.trigger('validate');
            var currentStep = nextStep - 1;
            //var tabContent = $scope.launchForm.find('#step' + currentStep);
            //var invalidFields = tabContent.find('[data-invalid]');
            //if (invalidFields.length || $scope.isNotValid === true) {
            //    invalidFields.focus();
            if ($scope.isNotValid === true) {
                $event.preventDefault();
                // Handle the case where the tab was clicked to visit the previous step
                if ($scope.currentStepIndex > nextStep) {
                    $scope.currentStepIndex = nextStep;
                    $scope.checkRequiredInput();
                }
                return false;
            }
            if (nextStep == 2 && $scope.step1Invalid) { $scope.clearErrors(2); $scope.step1Invalid = false; }
            if (nextStep == 3 && $scope.step2Invalid) { $scope.clearErrors(3); $scope.step2Invalid = false; }
            if (nextStep == 4 && $scope.step3Invalid) { $scope.clearErrors(4); $scope.step3Invalid = false; }

            // since above lines affects DOM, need to let that take affect first
            $timeout(function() {
            // If all is well, click the relevant tab to go to next step
            // since clicking invokes this method again (via ng-click) and
            // one ng action must complete before another can start
                var hash = "step"+nextStep;
                $("#wizard-tabs").children("dd").each(function() {
                    var link = $(this).find("a");
                    if (link.length !== 0) {
                        var id = link.attr("href").substring(1);
                        var $container = $("#" + id);
                        $(this).removeClass("active");
                        $container.removeClass("active");
                        if (id == hash || $container.find("#" + hash).length) {
                            $(this).addClass("active");
                            $container.addClass("active");
                        }
                    }
                });
                // Unhide appropriate step in summary
                $scope.summarySection.find('.step' + nextStep).removeClass('hide');
                $scope.currentStepIndex = nextStep;
                $scope.checkRequiredInput();
            },50);
        };
        $scope.clearErrors = function(step) {
            $('#step'+step).find('div.error').each(function(idx, val) {
                $(val).removeClass('error');
            });
        };
        $scope.createELB = function() {
        };
    })
;

