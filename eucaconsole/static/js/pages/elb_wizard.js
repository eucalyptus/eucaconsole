/**
 * @fileOverview Elastic Load Balancer Wizard JS
 * @requires AngularJS
 *
 * Note: Specify dependencies array in base_elb_wizard.js
 *
 */

angular.module('ELBWizard', [
    'EucaConsoleUtils', 'CreateBucketDialog', 'MagicSearch', 'ELBSecurityPolicyEditor',
    'TagEditorModule', 'ELBListenerEditor', 'ELBSecurityGroupRulesWarning']
).controller('ELBWizardCtrl', function ($scope, $http, $timeout, eucaHandleError,
                                        eucaUnescapeJson, eucaFixHiddenTooltips,
                                        eucaCheckELBSecurityGroupRules) {
    $scope.thisForm = undefined;
    $scope.urlParams = undefined;
    $scope.resourceName  = '';
    $scope.totalSteps = 0;
    $scope.currentStepIndex = 0;
    $scope.isValidationError = true;
    $scope.tabList = [];
    $scope.invalidSteps = [];
    $scope.stepClasses = [];
    $scope.summaryDisplays = [];
    $scope.elbForm = undefined;
    $scope.urlParams = undefined;
    $scope.isNotValid = true;
    $scope.securityGroupJsonEndpoint = '';
    $scope.elbName = '';
    $scope.listenerArray = [];
    $scope.vpcNetwork = '';
    $scope.vpcNetworkName = '';
    $scope.vpcSubnets = [];
    $scope.vpcSubnetNames = [];
    $scope.vpcSubnetChoices = {};
    $scope.vpcSubnetList = [];
    $scope.securityGroups = [];  // Selected security group ids (e.g. ["sg-123456", ...])
    $scope.securityGroupNames = [];  // Selected security group names (e.g. ["sgroup-one", ...])
    $scope.securityGroupChoices = {};  // id/name mapping of security group choices (e.g. {"sg-123": 'foo', ...})
    $scope.securityGroupCollection = [];  // Security group object choices
    $scope.selectedSecurityGroups = [];  // Selected security group objects
    $scope.loadBalancerInboundPorts = [];
    $scope.loadBalancerOutboundPorts = [];
    $scope.availabilityZones = [];
    $scope.availabilityZoneChoices = {};
    $scope.instanceList = [];
    $scope.crossZoneEnabled = true;
    $scope.protocolList = []; 
    $scope.pingProtocol = '';
    $scope.pingPort = '';
    $scope.pingPath = '';
    $scope.responseTimeout = '';
    $scope.timeBetweenPings = '';
    $scope.failuresUntilUnhealthy = '';
    $scope.passesUntilHealthy = '';
    $scope.canListCertificates = true;
    $scope.certificateTab = 'SSL';
    $scope.certificateRadioButton = '';
    $scope.certificateARN = '';
    $scope.certificateName = '';
    $scope.newCertificateName = '';
    $scope.privateKey = '';
    $scope.publicKeyCertificate = '';
    $scope.certificateChain = '';
    $scope.tempListenerBlock = {};
    $scope.showsCertificateTabDiv = false;
    $scope.backendCertificateArray = [];
    $scope.backendCertificateName = '';
    $scope.backendCertificateBody = '';
    $scope.backendCertificateTextarea = '';
    $scope.isBackendCertificateNotComplete = true;
    $scope.hasDuplicatedBackendCertificate = false;
    $scope.classDuplicatedBackendCertificateDiv = '';
    $scope.classAddBackendCertificateButton = 'disabled';
    $scope.classUseThisCertificateButton = 'disabled';
    $scope.loggingEnabled = false;
    $scope.bucketName = '';
    $scope.bucketNameField = $('#bucket_name');
    $scope.bucketNameChoices = {};
    $scope.accessLoggingConfirmed = false;
    $scope.accessLogConfirmationDialog = $('#elb-bucket-access-log-dialog');
    $scope.accessLogConfirmationDialogKey = 'doNotShowAccessLogConfirmationAgain';
    $scope.instanceCounts = {};
    $scope.initController = function (optionsJson) {
        var options = JSON.parse(eucaUnescapeJson(optionsJson));
        $scope.setInitialValues(options);
        $scope.setWatcher();
        $scope.setFocus();
        // Workaround for the Bug in jQuery to prevent JS Uncaught TypeError
        // See http://stackoverflow.com/questions/27408501/ng-repeat-sorting-is-throwing-an-exception-in-jquery
        Object.getPrototypeOf(document.createComment('')).getAttribute = function() {};
    };
    $scope.setInitialValues = function (options) {
        if (options.hasOwnProperty('resource_name')) {
            $scope.resourceName = options.resource_name;
        }
        if (options.hasOwnProperty('wizard_tab_list')) {
            $scope.tabList = options.wizard_tab_list;
        }
        $scope.totalSteps = $scope.tabList.length;
        $scope.thisForm = $('#' + $scope.resourceName + '-form');
        $scope.urlParams = $.url().param();
        $scope.currentStepIndex = 0;
        $scope.isValidationError = true;
        $scope.invalidSteps = Array.apply(undefined, Array($scope.totalSteps));
        angular.forEach($scope.invalidSteps, function(a, index){
            $scope.invalidSteps[index] = true;
        });
        $scope.invalidSteps[0] = false;
        $scope.stepClasss = Array.apply(undefined, Array($scope.totalSteps));
        angular.forEach($scope.stepClasses, function(a, index){
            $scope.stepClasses[index] = '';
        });
        $scope.stepClasses[$scope.currentStepIndex] = 'active';
        $scope.summaryDisplays = Array.apply(undefined, Array($scope.totalSteps));
        angular.forEach($scope.summaryDisplays, function(a, index){
            $scope.summaryDisplays[index] = false;
        });
        $scope.summaryDisplays[$scope.currentStepIndex] = true;
        var certArnField = $('#certificate_arn');
        $scope.bucketNameChoices = options.bucket_choices;
        $scope.existingCertificateChoices = options.existing_certificate_choices;
        $scope.elbForm = $('#elb-form');
        $scope.urlParams = $.url().param();
        $scope.isNotValid = true;
        $scope.securityGroupJsonEndpoint = options.securitygroups_json_endpoint;
        if (options.hasOwnProperty('protocol_list')) {
            $scope.protocolList = options.protocol_list;
            if ($scope.protocolList instanceof Array && $scope.protocolList.length > 0) {
                $scope.pingProtocol = $scope.protocolList[0].name;
            }
        }
        if (options.hasOwnProperty('default_vpc_network')) {
            $scope.vpcNetwork = options.default_vpc_network;
        }
        if (options.hasOwnProperty('availability_zone_choices')) {
            $scope.availabilityZoneList = options.availability_zone_choices;
            $scope.updateAvailabilityZoneChoices();
        }
        if (options.hasOwnProperty('vpc_subnet_choices')) {
            $scope.vpcSubnetList = options.vpc_subnet_choices;
            $scope.updateVPCSubnetChoices();
        }
        $scope.listenerArray = [];
        $scope.crossZoneEnabled = true;
        $scope.pingProtocol = 'HTTP';
        $scope.pingPort = 80;
        $scope.pingPath = '/';
        $scope.responseTimeout = 5;
        $scope.timeBetweenPings = 30;
        $scope.failuresUntilUnhealthy = 2;
        $scope.passesUntilHealthy = 2;
        $scope.showsCertificateTabDiv = false;
        $scope.certificateTab = 'SSL';
        $scope.certificateRadioButton = 'existing';
        $scope.backendCertificateArray = [];
        if ($('#hidden_backend_certificates').length > 0) {
            $scope.backendCertificateTextarea = $('#hidden_backend_certificates');
        }
        $scope.isBackendCertificateNotComplete = true;
        $scope.hasDuplicatedBackendCertificate = false;
        $scope.classDuplicatedBackendCertificateDiv = '';
        $scope.classAddBackendCertificateButton = 'disabled';
        $scope.classUseThisCertificateButton = 'disabled';
        // timeout is needed to wait for the elb listener directive to be initialized
        if (certArnField.children('option').length > 0) {
            $scope.certificateName = certArnField.children('option').first().text();
            $scope.certificateARN = certArnField.children('option').first().val();
        }
        $scope.canListCertificates = options.can_list_certificates;
        $scope.initChosenSelectors();
    };
    $scope.setWatcher = function (){
        $scope.$watch('currentStepIndex', function(newVal, oldVal){
            if( $scope.currentStepIndex !== 0 ){
                $scope.setWizardFocus($scope.currentStepIndex);
            }
            $scope.$broadcast('currentStepIndexUpdate', $scope.currentStepIndex);
        });
        $scope.$on('requestValidationCheck', function($event) {
            var currentStepID = $scope.currentStepIndex + 1;
            $scope.existInvalidFields(currentStepID);
        });
        $(document).on('open.fndtn.reveal', '[data-reveal]', function () {
            // When a dialog opens, reset the progress button status
            $(this).find('.dialog-submit-button').css('display', 'block');
            $(this).find('.dialog-progress-display').css('display', 'none');
            // Broadcast initModal signal to trigger the modal initialization
            $scope.$broadcast('initModal');
        });
        $(document).on('submit', '[data-reveal] form', function () {
            // When a dialog is submitted, display the progress button status
            $(this).find('.dialog-submit-button').css('display', 'none');
            $(this).find('.dialog-progress-display').css('display', 'block');
        });
        $(document).on('closed.fndtn.reveal', '[data-reveal]', function () {
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
        eucaFixHiddenTooltips();
        $(document).on('click', '#security-policy-dialog-submit-btn', function () {
            $scope.isNotChanged = false;
            $scope.$apply();
        });
        // Handle the next step tab click event
        $scope.$on('eventClickVisitNextStep', function($event, thisStep, nextStep) {
            $scope.checkRequiredInput(thisStep);
            $scope.processVisitNextStep(nextStep);
            $timeout(function() {
                // Workaround for the broken placeholer message issue
                // Wait until the rendering of the new tab page is complete
                $('#zone').trigger("chosen:updated");
                $('#vpc_subnet').trigger('chosen:updated');
                $scope.isHelpExpanded = false;
            });
        });
        $scope.$on('currentStepIndexUpdate', function($event, thisStepIndex) {
            $scope.checkRequiredInput(thisStepIndex+1);
        });
        $scope.$on('eventUpdateListenerArray', function ($event, listenerArray) {
            $scope.listenerArray = listenerArray;
        });
        $scope.$on('eventOpenSelectCertificateModal', function ($event, fromProtocol, toProtocol, fromPort, toPort, certificateTab) {
            if ((fromProtocol === 'HTTPS' || fromProtocol === 'SSL') &&
                (toProtocol === 'HTTPS' || toProtocol === 'SSL')) {
                $scope.showsCertificateTabDiv = true;
            } else {
                $scope.showsCertificateTabDiv = false;
            }
            $scope.tempListenerBlock = {
                'fromProtocol': fromProtocol,
                'fromPort': fromPort,
                'toProtocol': toProtocol,
                'toPort': toPort
            };
            $scope.certificateTab = certificateTab;
            $scope.openSelectCertificateModal();
        });
        $scope.$on('eventUpdateSelectedInstanceList', function ($event, instanceList) {
            $scope.instanceList = instanceList;
        });
        $scope.$on('eventUpdateAvailabilityZones', function ($event, availabilityZones) {
            $scope.availabilityZones = availabilityZones;
        });
        $scope.$on('eventUpdateVPCSubnets', function ($event, vpcSubnets) {
            $scope.vpcSubnets = vpcSubnets;
        });
        $scope.$watch('elbName', function (newVal, oldVal){
            $scope.checkRequiredInput(1);
        });
        $scope.$watch('vpcNetwork', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                $scope.availabilityZones = [];
                $scope.vpcSubnets = [];
                $scope.securityGroups = [];
                $scope.updateVPCNetworkName();
                $scope.getAllSecurityGroups($scope.vpcNetwork);
                $scope.updateVPCSubnetChoices();
                $scope.checkRequiredInput(2);
                $scope.$broadcast('eventWizardUpdateVPCNetwork', $scope.vpcNetwork);
                $timeout(function(){
                    if ($('#securitygroup_chosen').length === 0) {
                        $('#securitygroup').chosen({'width': '100%', search_contains: true});
                    }
                });
            }
        }, true);
        $scope.$watch('securityGroups', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                $scope.updateSecurityGroupNames();
                $scope.checkRequiredInput(2);
                // Update the VPC network on the instance selector when security group is updated
                $scope.$broadcast('eventWizardUpdateVPCNetwork', $scope.vpcNetwork);
            }
        }, true);
        $scope.$watch('securityGroupCollection', function (newVal, oldVal) {
            $scope.updateSecurityGroupChoices();
        }, true);
        $scope.$watch('availabilityZones', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                if ($scope.vpcNetwork === 'None') { 
                    if ($scope.currentStepIndex === 3) {
                        $scope.checkRequiredInput(3);
                    }
                    $scope.$broadcast('eventWizardUpdateAvailabilityZones', $scope.availabilityZones);
                }
            }
        }, true);
        $scope.$watch('vpcSubnets', function (newVal, oldVal) {
            $scope.updateVPCSubnetNames();
            if ($scope.vpcNetwork !== 'None') { 
                $scope.checkRequiredInput(3);
                $scope.$broadcast('eventWizardUpdateVPCSubnets', $scope.vpcSubnets);
            }
        }, true);
        $scope.$watch('instanceList', function (newValue, oldValue) {
            if ($scope.currentStepIndex === 3) {
                $scope.checkRequiredInput(3);
            }
            if ($scope.vpcNetwork !== 'None') { 
                $scope.updateVPCSubnetChoices();
            } else {
                $scope.updateAvailabilityZoneChoices();
            }
        }, true);
        $scope.$watch('listenerArray', function (newVal, oldVal) {
            if (newVal.length) {
                $scope.pingProtocol = newVal[0].toProtocol;
                $scope.pingPort = newVal[0].toPort;
            } else {
                $scope.pingProtocol = 'HTTP';
                $scope.pingPort = 80;
            }
        }, true);
        $scope.$watch('pingPort', function (newVal, oldVal){
            $scope.checkRequiredInput(4);
        });
        $scope.$watch('responseTimeout', function (newVal, oldVal){
            $scope.checkRequiredInput(4);
        });
        $scope.$watch('certificateTab', function (newVal, oldVal) {
            $scope.adjustSelectCertificateModalTabDisplay();
            $scope.setClassUseThisCertificateButton();
        });
        $scope.$watch('certificateARN', function(newVal, oldVal){
            var certArnField = $('#certificate_arn');
            var hiddenArnInput = $('#hidden_certificate_arn_input');
            // Find the certficate name when selected on the select certificate dialog
            if (certArnField.find('option:selected').length > 0) {
                $scope.certificateName = certArnField.find('option:selected').text();
            }
            // Assign the certificate ARN value as hidden input
            if (hiddenArnInput.length > 0) {
                hiddenArnInput.val($scope.certificateARN);
            }
            $scope.$broadcast('eventUpdateCertificateARN', $scope.certificateARN, $scope.tempListenerBlock);
        });
        $scope.$watch('certificateName', function(newVal, oldVal){
            // Broadcast the certificate name change to the elb listener directive
            $scope.$broadcast('eventUpdateCertificateName', $scope.certificateName);
        });
        $scope.$watch('certificateRadioButton', function(newVal, oldVal){
            $scope.setClassUseThisCertificateButton();
        });
        $scope.$watch('newCertificateName', function(newVal, oldVal){
            $scope.setClassUseThisCertificateButton();
        });
        $scope.$watch('privateKey', function(newVal, oldVal){
            $scope.setClassUseThisCertificateButton();
        });
        $scope.$watch('publicKeyCertificate', function(newVal, oldVal){
            $scope.setClassUseThisCertificateButton();
        });
        $scope.$watch('backendCertificateName', function (newVal, oldVal) {
            $scope.checkAddBackendCertificateButtonCondition(); 
        });
        $scope.$watch('backendCertificateBody', function (newVal, oldVal) {
            $scope.checkAddBackendCertificateButtonCondition(); 
        });
        $scope.$watch('backendCertificateArray', function (newVal, oldVal) {
            $scope.syncBackendCertificates();
            $scope.checkAddBackendCertificateButtonCondition(); 
            $scope.setClassUseThisCertificateButton();
        }, true);
        $scope.$watch('isBackendCertificateNotComplete', function (newVal, oldVal) {
            $scope.setClassAddBackendCertificateButton();
        });
        $scope.$watch('hasDuplicatedBackendCertificate', function (newVal, oldVal) {
            $scope.setClassAddBackendCertificateButton();
            $scope.classDuplicatedBackendCertificateDiv = '';
            // timeout is needed for the DOM update to complete
            $timeout(function () {
                if ($scope.hasDuplicatedBackendCertificate === true) {
                    $scope.classDuplicatedBackendCertificateDiv = 'error';
                }
            });
        });
        $scope.$on('searchUpdated', function ($event, query) {
            // Relay the query search update signal
            $scope.$broadcast('eventQuerySearch', query);
        });
        $scope.$on('textSearch', function ($event, searchVal, filterKeys) {
            // Relay the text search update signal
            $scope.$broadcast('eventTextSearch', searchVal, filterKeys);
        });
        $scope.$watch('loggingEnabled', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                $scope.isNotChanged = false;
                if (newVal) {
                    if (Modernizr.localstorage && !localStorage.getItem($scope.accessLogConfirmationDialogKey)) {
                        $scope.accessLogConfirmationDialog.foundation('reveal', 'open');
                    }
                }
                // TODO: ensure this doesn't clear existing validation error
                $scope.isValidationError = newVal && !$scope.bucketName;
            }
        });
        $scope.$watch('isValidationError', function (newVal, oldVal) {
            console.log("validation error : "+newVal);
        });
        $scope.$watch('bucketName', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                $scope.isValidationError = $scope.loggingEnabled && !newVal;
            }
        });
        $scope.accessLogConfirmationDialog.on('opened.fndtn.reveal', function () {
            $scope.accessLoggingConfirmed = false;
            $scope.$apply();
        });
        $scope.accessLogConfirmationDialog.on('close.fndtn.reveal', function () {
            if (!$scope.accessLoggingConfirmed) {
                $scope.loggingEnabled = false;
                $scope.$apply();
            }
            $('#bucket_name').focus().closest('.columns').removeClass('error');
        });
    };
    $scope.setFocus = function () {
        $(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
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
        var tabElement = $(document).find('#tabStep'+(stepIdx+1)).get(0);
        if (!!tabElement) {
            tabElement.focus();
        }
    };
    // return true if exists invalid input fields on 'step' page
    // also set the focus on the invalid field
    $scope.existInvalidFields = function(step) {
        if ($scope.thisForm === undefined) {
            return true;
        }
        $scope.thisForm.trigger('validate');
        var tabContent = $scope.thisForm.find('#step' + step);
        var invalidFields = tabContent.find('[data-invalid]');
        invalidFields.focus();
        if (invalidFields.length > 0 || $('#step' + step).find('div.error').length > 0) {
            $scope.isValidationError = true;
        } else {
            $scope.isValidationError = false;
        }
        return $scope.isValidationError;
    };
    $scope.visitStep = function($event, step) {
        $event.preventDefault();
        var nextStep = step;
        // In case of non-rendered step, jump forward
        if ($scope.tabList[step].render === false) {
            nextStep = step + 1;
        }
        $scope.$broadcast('eventClickVisitNextStep', $scope.currentStepIndex+1, nextStep);
    };
    $scope.processVisitNextStep = function(nextStep) {
        // Check for form validation before proceeding to next step
        var currentStepID = $scope.currentStepIndex + 1;
        if (nextStep < $scope.currentStepIndex) {
            // Case of clicking the tab direct to go backward step
            // No validation check is needed when stepping back
            $timeout(function() {
                $scope.updateStep(nextStep);
                $scope.$broadcast('currentStepIndexUpdate', $scope.currentStepIndex);
            });
        } else if ($scope.isValidationError === true || $scope.existInvalidFields(currentStepID)) {
            // NOT OK TO CHANGE TO NEXT STEP
            // NOTE: Need to handle the case where the tab was clicked to visit the previous step
            //
            // Broadcast signal to trigger input field check on the currentStepIndex page 
            $scope.$broadcast('currentStepIndexUpdate', $scope.currentStepIndex);
        } else { // OK to switch
            // Since the operations above affects DOM,
            // need to wait after Foundation's update for Angular to process 
            $timeout(function() {
                // clear the invalidSteps flag
                if ($scope.invalidSteps[nextStep]) {
                    $scope.clearErrors(nextStep);
                    $scope.invalidSteps[nextStep] = false;
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
            var hash = "step" + (step+1) ;
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
        $scope.stepClasses[step] = 'active';
        // Display the summary section 
        $scope.showSummarySecton(step); 
        // Update the current step index
        $scope.currentStepIndex = step;
    };
    // Display appropriate step in summary
    $scope.showSummarySecton = function(step) {
        $scope.summaryDisplays[step] = true;
    };
    $scope.clearErrors = function(step) {
        $('#step'+step).find('div.error').each(function(idx, val) {
            $(val).removeClass('error');
        });
    };
    $scope.initChosenSelectors = function () {
        $('#vpc_subnet').chosen({'width': '100%', search_contains: true});
        $('#securitygroup').chosen({'width': '100%', search_contains: true});
        $('#zone').chosen({'width': '100%', search_contains: true});
    };
    $scope.checkRequiredInput = function (step) {
        $scope.isNotValid = false;
        if (step === 1) {
            var elbListenerTextArea = $('#elb-listener');
            if ($scope.elbName === '' || $scope.elbName === undefined) {
                $scope.isNotValid = true;
            } else if (elbListenerTextArea.length > 0) {
                if (elbListenerTextArea.val() === '' || elbListenerTextArea.val() === '[]') {
                    $scope.isNotValid = true;
                }
            }
            // Handle the unsaved listener issue
            if( $('#from-port-input').val() !== '' ){
                $('#unsaved-listener-warn-modal').foundation('reveal', 'open');
                $scope.isNotValid = true;
            }
        } else if (step === 2) {
        } else if (step === 3) {
            if ($scope.vpcNetwork !== 'None') { 
                if ($scope.vpcSubnets.length === 0) {
                    $scope.isNotValid = true;
                }
            } else {
                if ($scope.availabilityZones.length === 0 && $scope.vpcSubnets.length === 0) {
                    $scope.isNotValid = true;
                }
            }
        } else if (step === 4) {
            // elb name check is needed for the final tab validation
            if ($scope.elbName === '' || $scope.elbName === undefined) {
                $scope.isNotValid = true;
            } else if ($scope.pingPort <= 0 || $scope.pingPort === undefined) {
                $scope.isNotValid = true;
            } else if ($scope.responseTimeout <= 0 || $scope.responseTimeout === undefined) {
                $scope.isNotValid = true;
            }
        }
        $scope.isValidationError = $scope.isNotValid;
    };
    $scope.getAllSecurityGroups = function (vpc) {
        var csrf_token = $('#csrf_token').val();
        var data = "csrf_token=" + csrf_token + "&vpc_id=" + vpc;
        $http({
            method:'POST', url:$scope.securityGroupJsonEndpoint, data:data,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'}
        }).success(function(oData) {
            var results = oData ? oData.results : [];
            $scope.securityGroupCollection = results;
        }).error(function (oData) {
            eucaHandleError(oData, status);
        });
    };
    $scope.updateSecurityGroupChoices = function () {
        $scope.securityGroupChoices = {};
        if ($.isEmptyObject($scope.securityGroupCollection)) {
            return;
        }
        $scope.securityGroups = [];
        angular.forEach($scope.securityGroupCollection, function(sGroup){
            var securityGroupName = sGroup.name;
            if (sGroup.name.length > 45) {
                securityGroupName = sGroup.name.substr(0, 45) + "...";
            }
            $scope.securityGroupChoices[sGroup.id] = securityGroupName;
        }); 
        // Timeout is needed for chosen to react after Angular updates the options
        $timeout(function(){
            $('#securitygroup').trigger('chosen:updated');
        }, 500);
    };
    $scope.updateAvailabilityZoneChoices = function () {
        $scope.availabilityZoneChoices = {};
        angular.forEach($scope.availabilityZoneList, function(zone){
            var instanceCount = 0;
            angular.forEach($scope.instanceList, function(instance) {
                if (instance.placement === zone.name) {
                    instanceCount += 1;
                } 
            });
            $scope.availabilityZoneChoices[zone.name] = zone.name +
                ": " + instanceCount + " instances";
        });
        // Timeout is needed for chosen to react after Angular updates the options
        $timeout(function(){
            if ($scope.availabilityZones.length === 0) {
                $scope.availabilityZones.push(Object.keys($scope.availabilityZoneChoices)[0]);
            }
            $('#zone').trigger('chosen:updated');
        }, 500);
    };
    $scope.updateVPCSubnetChoices = function () {
        $scope.vpcSubnetChoices = {};
        angular.forEach($scope.vpcSubnetList, function(subnet){
            if (subnet.vpc_id === $scope.vpcNetwork) {
                var instanceCount = 0;
                angular.forEach($scope.instanceList, function(instance) {
                    if (instance.subnet_id === subnet.id) {
                        instanceCount += 1;
                    } 
                });
                $scope.vpcSubnetChoices[subnet.id] = 
                    subnet.cidr_block + ' (' + subnet.id + ') | ' + 
                    subnet.availability_zone + ": " + instanceCount + " instances";
            }
        });
        if ($scope.vpcSubnetChoices.length === 0) {
            $scope.vpcSubnetChoices.None = $('#hidden_vpc_subnet_empty_option').text();
            $scope.vpcSubnets = [];
            $scope.vpcSubnets.push('None');
        }
        // Timeout is needed for chosen to react after Angular updates the options
        $timeout(function(){
            $('#vpc_subnet').trigger('chosen:updated');
        }, 500);
    };
    $scope.updateVPCNetworkName = function () {
        var vpcNetworkSelectOptions = $('#vpc_network option');
        if (vpcNetworkSelectOptions.length > 0) {
            vpcNetworkSelectOptions.each(function () {
                if ($(this).val() === $scope.vpcNetwork) {
                    $scope.vpcNetworkName = $(this).text();
                }
            });
        }
    };
    $scope.updateSecurityGroupNames = function () {
        $scope.securityGroupNames = [];
        angular.forEach($scope.securityGroups, function (sGroup) {
            $scope.securityGroupNames.push($scope.securityGroupChoices[sGroup]);
        });
    };
    $scope.updateVPCSubnetNames = function () {
        $scope.vpcSubnetNames = [];
        angular.forEach($scope.vpcSubnets, function (vpcSubnet) {
            angular.forEach($scope.vpcSubnetList, function (subnet) {
                if (subnet.id === vpcSubnet) {
                    var vpcSubnetName =  subnet.cidr_block + ' (' + subnet.id + ') | ' + subnet.availability_zone;
                    $scope.vpcSubnetNames.push(vpcSubnetName);
                }
            });
        });
    };
    $scope.getInstanceCount = function (type, group) {
        var count = 0;
        angular.forEach($scope.instanceList, function (instance) {
            if (type === 'ZONE' && instance.placement === group) {
                count += 1;
            } else if (type === 'SUBNET' && instance.subnet_id === group) {
                count += 1;
            }
        });
        return count;
    };
    $scope.openSelectCertificateModal = function () {
        var modal = $('#select-certificate-modal');
        var certArnField = $('#certificate_arn');
        if (modal.length > 0) {
            modal.foundation('reveal', 'open');
            $scope.certificateRadioButton = $scope.canListCertificates ? 'existing' : 'new';
            $('#certificate-type-radio-existing').prop('checked', true);
            angular.forEach($scope.listenerArray, function (block) {
                if (block.fromPort === $scope.tempListenerBlock.fromPort &&
                    block.toPort === $scope.tempListenerBlock.toPort) {
                    $scope.certificateARN = block.certificateARN;
                    $scope.certificateName = block.certificateName;
                }
            });
            certArnField.val($scope.certificateARN);
            // Remove any empty options created by Angular model issue
            certArnField.find('option').each(function () {
                if ($(this).text() === '') {
                    $(this).remove();
                }
            });
        }
    };
    $scope.selectCertificateTab = function ($event, tab) {
        $event.preventDefault();
        $scope.certificateTab = tab;
    };
    $scope.adjustSelectCertificateModalTabDisplay = function () {
        var sslTab = $('#select-certificate-modal-tab-ssl');
        var backendTab = $('#select-certificate-modal-tab-backend');
        sslTab.removeClass('active');
        backendTab.removeClass('active');
        if ($scope.certificateTab === 'SSL') {
            sslTab.addClass('active');
        } else {
            backendTab.addClass('active');
        }
    };
    $scope.createBackendCertificateArrayBlock = function () {
        return {
            'name': $scope.backendCertificateName,
            'certificateBody': $scope.backendCertificateBody
        };
    };
    $scope.addBackendCertificate = function ($event) {
        $event.preventDefault();
        $scope.checkAddBackendCertificateButtonCondition(); 
        // timeout is needed for all DOM updates and validations to be complete
        $timeout(function () {
            if( $scope.isBackendCertificateNotComplete === true || $scope.hasDuplicatedBackendCertificate === true){
                return false;
            }
            // Add the backend certificate 
            $scope.backendCertificateArray.push($scope.createBackendCertificateArrayBlock());
            $scope.$emit('backendCertificateArrayUpdate');
            $scope.resetBackendCertificateValues();
        });
    };
    $scope.syncBackendCertificates = function () {
        if ($scope.backendCertificateTextarea.length > 0) {
            var backendCertificateJSON = JSON.stringify($scope.backendCertificateArray);
            $scope.backendCertificateTextarea.val(backendCertificateJSON);
        }
    };
    $scope.resetBackendCertificateValues = function () {
        // Remove the required attr from the body field to avoid false negative validation error
        // when the input fields are cleared
        $('#backend_certificate_body').removeAttr('required');
        $scope.backendCertificateName = '';
        $scope.backendCertificateBody = '';
        // timeout is needed for Foundation's validation to complete
        // re-insert the required attr to the input field
        $timeout(function () {
            $('#backend_certificate_body').attr('required', 'required');
        }, 1000);
    };
    $scope.removeBackendCertificate = function ($event, index) {
        $event.preventDefault();
        $scope.backendCertificateArray.splice(index, 1);
    };
    $scope.setClassAddBackendCertificateButton = function () {
        if ($scope.isBackendCertificateNotComplete === true || $scope.hasDuplicatedBackendCertificate === true) {
            $scope.classAddBackendCertificateButton = 'disabled';
        } else {
            $scope.classAddBackendCertificateButton = '';
        }
    };
    $scope.setClassUseThisCertificateButton = function () {
        if ($scope.certificateTab === 'SSL') {
            if ($scope.certificateRadioButton === 'existing') {
                $scope.classUseThisCertificateButton = '';
            } else {
                if ($scope.newCertificateName === undefined || $scope.newCertificateName === '') {
                    $scope.classUseThisCertificateButton = 'disabled';
                } else if ($scope.privateKey === undefined || $scope.privateKey === '') {
                    $scope.classUseThisCertificateButton = 'disabled';
                } else if ($scope.publicKeyCertificate === undefined || $scope.publicKeyCertificate === '') {
                    $scope.classUseThisCertificateButton = 'disabled';
                } else {
                    $scope.classUseThisCertificateButton = '';
                }
            }
        } else if ($scope.certificateTab === 'BACKEND') {
            if ($scope.backendCertificateArray.length === 0) {
                $scope.classUseThisCertificateButton = 'disabled';
            } else {
                $scope.classUseThisCertificateButton = '';
            }
        } else {
            $scope.classUseThisCertificateButton = 'disabled';
        }
    };
    $scope.checkAddBackendCertificateButtonCondition = function () {
        if ($scope.backendCertificateName === '' || $scope.backendCertificateName === undefined) {
            $scope.isBackendCertificateNotComplete = true;
        } else if ($scope.backendCertificateBody === '' || $scope.backendCertificateBody === undefined) {
            $scope.isBackendCertificateNotComplete = true;
        } else {
            $scope.isBackendCertificateNotComplete = false;
        }
        $scope.checkForDuplicatedBackendCertificate(); 
    };
    $scope.checkForDuplicatedBackendCertificate = function () {
        $scope.hasDuplicatedBackendCertificate = false;
        // Create a new array block based on the current user input on the panel
        var newBlock = $scope.createBackendCertificateArrayBlock();
        for( var i=0; i < $scope.backendCertificateArray.length; i++){
            // Compare the new array block with the existing ones
            if ($scope.compareBackendCertificates(newBlock, $scope.backendCertificateArray[i])) {
                $scope.hasDuplicatedBackendCertificate = true;
                return;
            }
        }
        return;
    };
    $scope.compareBackendCertificates = function (block1, block2) {
        return block1.name === block2.name;
    };
    $scope.handleCertificateCreate = function ($event, newCertURL) {
        $event.preventDefault();
        if ($scope.classUseThisCertificateButton === 'disabled') {
            return false;
        }
        if ($scope.certificateRadioButton === 'new') {
            $scope.createNewCertificate(newCertURL);
        }
        var modal = $('#select-certificate-modal');
        if (modal.length > 0) {
            modal.foundation('reveal', 'close');
            $scope.$broadcast('eventUseThisCertificate', $scope.certificateARN, $scope.certificateName);
        }
    };
    $scope.createNewCertificate = function (url) {
        var certForm = $('#select-certificate-form');
        var formData = certForm.serialize();
        $scope.certificateForm = certForm;
        $scope.certificateForm.trigger('validate');
        if (!$scope.certificateARN && !$scope.newCertificateName) {
            return false;
        }
        $http({
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            method: 'POST',
            url: url,
            data: formData
        }).success(function (oData) {
            Notify.success(oData.message);
            if (oData.id) {
                var newARN = oData.id;
                $('#certificate_arn').append($("<option></option>")
                    .attr("value", newARN)
                    .text($scope.newCertificateName));
                $scope.certificateARN = newARN;
                // timeout is needed for the select element to be updated with the new option
                $timeout(function () {
                    $scope.certificateName = $scope.newCertificateName;
                    // inform elb listener editor about the new certificate
                    $scope.$broadcast('eventUseThisCertificate', newARN, $scope.newCertificateName);
                });
            }
        }).error(function (oData) {
            eucaHandleError(oData, status);
        });
    };
    $scope.confirmEnableAccessLogs = function () {
        var modal = $('#elb-bucket-access-log-dialog');
        if (modal.find('#dont-show-again').is(':checked') && Modernizr.localstorage) {
            localStorage.setItem($scope.accessLogConfirmationDialogKey, true);
        }
        $scope.accessLoggingConfirmed = true;
        $scope.accessLogConfirmationDialog.foundation('reveal', 'close');
    };
    $scope.createELB = function ($event, confirmed) {
        confirmed = confirmed || false;
        var bucketNameField = $('#bucket_name');
        if (!$scope.isNotValid && !$scope.isValidationError) {
            // bucket name field requires special validation handling since it is conditionally required
            if (!$scope.loggingEnabled) {
                bucketNameField.removeAttr('required');
            } else {
                bucketNameField.attr('required');
            }
            $scope.checkSecurityGroupRules($event, confirmed);
        }
    };
    $scope.checkSecurityGroupRules = function ($event, confirmed) {
        var modal = $('#elb-security-group-rules-warning-modal');
        var inboundOutboundPortChecksPass;
        if ($scope.vpcNetwork === 'None') {  // Bypass rules check on non-VPC clouds
            $scope.elbForm.submit();
            return;
        }
        inboundOutboundPortChecksPass = eucaCheckELBSecurityGroupRules($scope);
        if (!confirmed && !inboundOutboundPortChecksPass) {
            modal.foundation('reveal', 'open');
            $event.preventDefault();
        } else {
            $scope.elbForm.submit();
        }
    };
})
    .directive('focusOnLoad', function ($timeout) {
        return {
            restrict: 'A',
            link: function (scope, elem) {
                $timeout(function () {
                    elem[0].focus();
                });
            }
        };
    })
;
