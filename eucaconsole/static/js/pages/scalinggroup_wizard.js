/**
 * @fileOverview Create Scaling Group wizard page JS
 * @requires AngularJS
 *
 */

// Scaling Group wizard includes the AutoScale Tag Editor
angular.module('ScalingGroupWizard', ['AutoScaleTagEditor'])
    .controller('ScalingGroupWizardCtrl', function ($scope) {
        $scope.form = $('#scalinggroup-wizard-form');
        $scope.scalingGroupName = '';
        $scope.launchConfig = '';
        $scope.healthCheckType = 'EC2';
        $scope.healthCheckPeriod = 120;
        $scope.minSize = 1;
        $scope.desiredCapacity = 1;
        $scope.maxSize = 1;
        $scope.urlParams = $.url().param();
        $scope.launchConfig = '';
        $scope.availZones = '';
        $scope.summarySection = $('.summary');
        $scope.currentStepIndex = 1;
        $scope.isNotValid = true;
        $scope.initChosenSelectors = function () {
            $('#launch_config').chosen({'width': '80%', search_contains: true});
            $('#load_balancers').chosen({'width': '80%', search_contains: true});
            $('#availability_zones').chosen({'width': '100%', search_contains: true});
        };
        $scope.setInitialValues = function () {
            $scope.availZones = $('#availability_zones').val();
        };
        $scope.initController = function (launchConfigCount) {
            $scope.initChosenSelectors();
            $scope.setInitialValues();
            $scope.setWatcher();
            $(document).ready(function () {
                $scope.displayLaunchConfigWarning(launchConfigCount);
            });
        };
        $scope.checkRequiredInput = function () {
            if( $scope.currentStepIndex == 1 ){ 
                $scope.isNotValid = false;
                if( $scope.scalingGroupName === '' || $scope.scalingGroupName === undefined ){
                    $scope.isNotValid = true;
                }else if( $scope.launchConfig === '' || $scope.launchConfig === undefined ){
                    $scope.isNotValid = true;
                }else if( $scope.minSize === '' || $scope.minSize === undefined ){
                    $scope.isNotValid = true;
                }else if( $scope.desiredCapacity === '' || $scope.desiredCapacity === undefined ){
                    $scope.isNotValid = true;
                }else if( $scope.maxSize === '' || $scope.maxSize === undefined ){
                    $scope.isNotValid = true;
                }
            }else if( $scope.currentStepIndex == 2 ){
                $scope.isNotValid = false;
                if( $scope.healthCheckPeriod === '' || $scope.healthCheckPeriod === undefined ){
                    $scope.isNotValid = true;
                }else if( $scope.availZones === '' || $scope.availZones === undefined ){
                    $scope.isNotValid = true;
                }
            }
        };
        $scope.setWatcher = function (){
            $scope.$watch('currentStepIndex', function(){
                 $scope.setWizardFocus($scope.currentStepIndex);
            });
            $scope.$watch('scalingGroupName', function(){
                $scope.checkRequiredInput();
            });
            $scope.$watch('launchConfig', function(){
                $scope.checkRequiredInput();
            });
            $scope.$watch('minSize', function(){
                $scope.checkRequiredInput();
            });
            $scope.$watch('desiredCapacity', function(){
                $scope.checkRequiredInput();
            });
            $scope.$watch('maxSize', function(){
                $scope.checkRequiredInput();
            });
            $scope.$watch('healthCheckPeriod', function(){
                $scope.checkRequiredInput();
            });
            $scope.$watch('availZones', function(){
                $scope.checkRequiredInput();
            });
        }
        $scope.setWizardFocus = function (stepIdx) {
            var modal = $('div').filter("#step" + stepIdx);
            var inputElement = modal.find('input[type!=hidden]').get(0);
            var textareaElement = modal.find('textarea[class!=hidden]').get(0);
            var selectElement = modal.find('select').get(0);
            var modalButton = modal.find('button').get(0);
            if (!!textareaElement){
                textareaElement.focus();
            } else if (!!inputElement) {
                inputElement.focus();
            } else if (!!selectElement) {
                selectElement.focus();
            } else if (!!modalButton) {
                modalButton.focus();
            }
        };
        $scope.visitNextStep = function (nextStep, $event) {
            // Trigger form validation before proceeding to next step
            $scope.form.trigger('validate');
            var currentStep = nextStep - 1,
                tabContent = $scope.form.find('#step' + currentStep),
                invalidFields = tabContent.find('[data-invalid]');
            if (invalidFields.length > 0 || $scope.isNotValid === true) {
                invalidFields.focus();
                $event.preventDefault();
                return false;
            }
            // If all is well, click the relevant tab to go to next step
            $('#tabStep' + nextStep).click();
            $scope.currentStepIndex = nextStep;
            $scope.checkRequiredInput();
            // Unhide step 2 of summary
            if (nextStep === 2) {
                $scope.summarySection.find('.step2').removeClass('hide');
            }
        };
        $scope.handleSizeChange = function () {
            // Adjust desired/max based on min size change
            if ($scope.desiredCapacity < $scope.minSize) {
                $scope.desiredCapacity = $scope.minSize;
            }
            if ($scope.maxSize < $scope.desiredCapacity) {
                $scope.maxSize = $scope.desiredCapacity;
            }
        };
        $scope.displayLaunchConfigWarning = function (launchConfigCount) {
            if (launchConfigCount === 0) {
                $('#create-warn-modal').foundation('reveal', 'open');
            }
        };
    })
;

