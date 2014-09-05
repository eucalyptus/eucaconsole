/**
 * @fileOverview Create Scaling Group wizard page JS
 * @requires AngularJS
 *
 */

// Scaling Group wizard includes the AutoScale Tag Editor
angular.module('ScalingGroupWizard', ['AutoScaleTagEditor'])
    .controller('ScalingGroupWizardCtrl', function ($scope, $timeout) {
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
        $scope.vpcNetwork = '';
        $scope.vpcNetworkName = '';
        $scope.vpcSubnets = [];
        $scope.vpcSubnetNames = '';
        $scope.vpcSubnetList = {};
        $scope.vpcSubnetChoices = {};
        $scope.availZones = '';
        $scope.summarySection = $('.summary');
        $scope.currentStepIndex = 1;
        $scope.isNotValid = true;
        $scope.initChosenSelectors = function () {
            $('#launch_config').chosen({'width': '80%', search_contains: true});
            $('#load_balancers').chosen({'width': '80%', search_contains: true});
            $('#availability_zones').chosen({'width': '100%', search_contains: true});
            $('#vpc_subnet').chosen({'width': '100%', search_contains: true});
        };
        $scope.setInitialValues = function () {
            $scope.availZones = $('#availability_zones').val();
        };
        $scope.checkLaunchConfigParam = function () {
            if( $('#hidden_launch_config_input').length > 0 ){
                $scope.launchConfig = $('#hidden_launch_config_input').val();
            }
        };
        $scope.initController = function (launchConfigCount, vpcSubnetJson) {
            vpcSubnetJson = vpcSubnetJson.replace(/__apos__/g, "\'").replace(/__dquote__/g, '\\"').replace(/__bslash__/g, "\\");
            $scope.vpcSubnetList = JSON.parse(vpcSubnetJson);
            $scope.initChosenSelectors();
            $scope.setInitialValues();
            $scope.checkLaunchConfigParam();
            $scope.setWatcher();
            $(document).ready(function () {
                $scope.displayLaunchConfigWarning(launchConfigCount);
            });
            // Timeout is needed for the chosen widget to initialize
            $timeout(function () {
                $scope.adjustVPCSubnetSelectAbide();
            }, 500);
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
            $scope.$watch('vpcNetwork', function () {
                $scope.updateVPCSubnetChoices();
                $scope.updateSelectedVPCNetworkName();
                $scope.adjustVPCSubnetSelectAbide();
            });
            $scope.$watch('vpcSubnets', function () { 
                $scope.updateSelectedVPCSubnetNames();
            });
        };
        $scope.adjustVPCSubnetSelectAbide = function () {
            // If VPC option is not chosen, remove the 'required' attribute
            // from the VPC subnet select field and set the value to be 'None'
            if ($scope.vpcNetwork == '') {
                $('#vpc_subnet').removeAttr('required');
                $('#vpc_subnet').find('option').first().attr("selected",true);
            } else {
                $('#vpc_subnet').find('option').first().removeAttr("selected");
                $('#vpc_subnet').attr("required", "required");
            }
        };
        $scope.updateVPCSubnetChoices = function () {
            var foundVPCSubnets = false;
            $scope.vpcSubnetChoices = {};
            $scope.vpcSubnets = [];
            angular.forEach($scope.vpcSubnetList, function (subnet) {
                if (subnet['vpc_id'] === $scope.vpcNetwork) {
                    $scope.vpcSubnetChoices[subnet['id']] = 
                        subnet['cidr_block'] + ' (' + subnet['id'] + ') | ' + subnet['availability_zone'];
                    foundVPCSubnets = true;
                }
            }); 
            if (!foundVPCSubnets) {
                $scope.vpcSubnetChoices['None'] = $('#vpc_subnet_empty_option').text();
            }
            // Timeout is need for the chosen widget to react after Angular has updated the option list
            $timeout(function() {
                $('#vpc_subnet').trigger('chosen:updated');
            }, 500);
        };
        $scope.updateSelectedVPCNetworkName = function () {
            var vpcNetworkOptions = $('select#vpc_network option');
            vpcNetworkOptions.each(function () {
                if ($(this).attr('value') == $scope.vpcNetwork) {
                    var vpcNetworkNameArray = $(this).text().split(' ');
                    vpcNetworkNameArray.pop();
                    $scope.vpcNetworkName = vpcNetworkNameArray.join(' ');
                } 
            });
        };
        $scope.updateSelectedVPCSubnetNames = function () {
            var foundVPCSubnets = false;
            $scope.vpcSubnetNames = [];
            angular.forEach($scope.vpcSubnets, function (subnetID) {
                angular.forEach($scope.vpcSubnetList, function (subnet) {
                    if (subnetID === subnet['id']) {
                       $scope.vpcSubnetNames.push(subnet['cidr_block']);
                    }
                });
            });
        }; 
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
                // Handle the case where the tab was clicked to visit the previous step
                if( $scope.currentStepIndex > nextStep){
                    $scope.currentStepIndex = nextStep;
                    $scope.checkRequiredInput();
                }
                return false;
            }
            // Handle the unsaved tag issue
            var existsUnsavedTag = false;
            $('input.taginput[type!="checkbox"]').each(function(){
                if($(this).val() !== ''){
                    existsUnsavedTag = true;
                }
            });
            if( existsUnsavedTag ){
                $event.preventDefault(); 
                $('#unsaved-tag-warn-modal').foundation('reveal', 'open');
                return false;
            }
            // since above lines affects DOM, need to let that take affect first
            $timeout(function() {
                // If all is well, hide current and show new tab without clicking
                // since clicking invokes this method again (via ng-click) and
                // one ng action must complete before another can start
                var hash = "step"+nextStep;
                $(".tabs").children("dd").each(function() {
                    var link = $(this).find("a");
                    if (link.length != 0) {
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
            });
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

