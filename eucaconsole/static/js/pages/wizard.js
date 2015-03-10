/**
 * @fileOverview Wizard JS
 * @requires AngularJS
 *
 */

var wizardApp = angular.module('Wizard', ['EucaConsoleUtils', 'MagicSearch'])
    .controller('WizardCtrl', function ($scope, $http, $timeout, eucaHandleError, eucaUnescapeJson) {
        $scope.elbForm = undefined;
        $scope.urlParams = undefined;
        $scope.resourceName  = '';
        $scope.totalSteps = 0;
        $scope.currentStepIndex = 1;
        $scope.isValidationError = true;
        $scope.invalidSteps = [];
        $scope.stepClasses = [];
        $scope.summaryDisplays = [];
        $scope.initController = function (resourceName, totalSteps) {
            $scope.setInitialValues(resourceName, totalSteps);
            $scope.setWatcher();
            $scope.setFocus();
        };
        $scope.setInitialValues = function (resourceName, totalSteps) {
            $scope.resourceName = resourceName;
            $scope.totalSteps = totalSteps;
            $scope.elbForm = $('#' + $scope.resourceName + '-form');
            $scope.urlParams = $.url().param();
            $scope.currentStepIndex = 1;
            $scope.isValidationError = true;
            $scope.invalidSteps = Array.apply(undefined, Array($scope.totalSteps));
            angular.forEach($scope.invalidSteps, function(a, index){
                $scope.invalidSteps[index] = true;
            });
            $scope.stepClasss = Array.apply(undefined, Array($scope.totalSteps));
            angular.forEach($scope.stepClasses, function(a, index){
                $scope.stepClasses[index] = '';
            });
            $scope.stepClasses[$scope.currentStepIndex - 1] = 'active';
            $scope.summaryDisplays = Array.apply(undefined, Array($scope.totalSteps));
            angular.forEach($scope.summaryDisplays, function(a, index){
                $scope.summaryDisplays[index] = false;
            });
            $scope.summaryDisplays[$scope.currentStepIndex - 1] = true;
        };
        $scope.setWatcher = function (){
            $scope.$watch('currentStepIndex', function(){
                if( $scope.currentStepIndex != 1 ){
                    $scope.setWizardFocus($scope.currentStepIndex);
                }
                $scope.$broadcast('currentStepIndexUpdate', $scope.currentStepIndex);
            });
            $scope.$on('eventProcessVisitNextStep', function($event, nextStep) {
                $scope.processVisitNextStep(nextStep);
            });
            $scope.$on('updateValidationErrorStatus', function($event, flag) {
                $scope.isValidationError = flag;
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
            $(document).on('closed', '[data-reveal]', function () {
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
        // return true if exists invalid input fields on 'step' page
        // also set the focus on the invalid field
        $scope.existInvalidFields = function(step) {
            if ($scope.elbForm === undefined) {
                return true;
            }
            $scope.elbForm.trigger('validate');
            var tabContent = $scope.elbForm.find('#step' + step);
            var invalidFields = tabContent.find('[data-invalid]');
            invalidFields.focus();
            if (invalidFields.length > 0) {
                return true;
            } else {
                return false;
            }
        };
        $scope.visitNextStep = function($event, nextStep) {
            $event.preventDefault();
            $scope.$broadcast('eventClickVisitNextStep', nextStep);
        };
        $scope.processVisitNextStep = function(nextStep) {
            var currentStep = nextStep - 1;
            var invalidStepsIndex = currentStep - 1;

            // Check for form validation before proceeding to next step
            if ($scope.existInvalidFields(currentStep) || $scope.isValidationError === true) {
                // Handle the case where the tab was clicked to visit the previous step
                if ($scope.currentStepIndex > nextStep) {
                    $scope.currentStepIndex = nextStep;
                }
                // Broadcast signal to trigger input field check on the currentStepIndex page 
                $scope.$broadcast('currentStepIndexUpdate', $scope.currentStepIndex);
            } else { // OK to switch
                // Since the operations above affects DOM,
                // need to wait after Foundation's update for Angular to process 
                $timeout(function() {
                    // clear the invalidSteps flag
                    if ($scope.invalidSteps[invalidStepsIndex]) {
                        $scope.clearErrors(nextStep);
                        $scope.invalidSteps[invalidStepsIndex] = false;
                    }
                    $scope.updateStep(nextStep);
                    // Broadcast signal to trigger input field check on the currentStepIndex page 
                    $scope.$broadcast('currentStepIndexUpdate', $scope.currentStepIndex);
                });
            }
        };
        $scope.updateStep = function(step) {
            // Adjust the tab classes to match Foundation's display 
            $("#wizard-tabs").children("dd").each(function() {
                // Clear 'active' class from all tabs
                $(this).removeClass("active");
                // Set 'active' class on the current tab
                var hash = "step" + step;
                var link = $(this).find("a");
                if (link.length > 0) {
                    var id = link.attr("href").substring(1);
                    if (id == hash) {
                        $(this).addClass("active");
                    }
                }
            });
            // Clear all step classes
            angular.forEach($scope.stepClasses, function(a, index){
                $scope.stepClasses[index] = '';
            });
            // Activate the target step class
            $scope.stepClasses[step - 1] = 'active';
            // Display the summary section 
            $scope.showSummarySecton(step); 
            // Update the current step index
            $scope.currentStepIndex = step;
        };
        // Display appropriate step in summary
        $scope.showSummarySecton = function(step) {
            $scope.summaryDisplays[step - 1] = true;
        };
        $scope.clearErrors = function(step) {
            $('#step'+step).find('div.error').each(function(idx, val) {
                $(val).removeClass('error');
            });
        };
    })
;

