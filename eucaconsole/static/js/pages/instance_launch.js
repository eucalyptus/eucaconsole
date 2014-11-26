/**
 * @fileOverview Launch Instance page JS
 * @requires AngularJS
 *
 */

// Launch Instance page includes the Tag Editor, the Image Picker, BDM editor, and security group rules editor
angular.module('LaunchInstance', ['TagEditor', 'BlockDeviceMappingEditor', 'ImagePicker', 'SecurityGroupRules', 'EucaConsoleUtils'])
    .controller('LaunchInstanceCtrl', function ($scope, $http, $timeout, eucaHandleError, eucaUnescapeJson) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.launchForm = $('#launch-instance-form');
        $scope.tagsObject = {};
        $scope.imageID = '';
        $scope.imageName = '';
        $scope.imagePlatform = '';
        $scope.imageRootDeviceType = '';
        $scope.urlParams = $.url().param();
        $scope.summarySection = $('.summary');
        $scope.instanceNumber = 1;
        $scope.instanceNames = [];
        $scope.instanceVPC = '';
        $scope.instanceVPCName = '';
        $scope.subnetVPC = 'None';
        $scope.vpcSubnetList = {};
        $scope.vpcSubnetChoices = {};
        $scope.keyPair = '';
        $scope.keyPairChoices = {};
        $scope.newKeyPairName = '';
        $scope.keyPairModal = $('#create-keypair-modal');
        $scope.isLoadingKeyPair = false;
        $scope.securityGroups = [];
        $scope.securityGroupsRules = {};
        $scope.securityGroupCollection = {};
        $scope.securityGroupJsonEndpoint = '';
        $scope.securityGroupsRulesJsonEndpoint = '';
        $scope.selectedGroupRules = {};
        $scope.securityGroupModal = $('#create-securitygroup-modal');
        $scope.securityGroupForm = $('#create-securitygroup-form');
        $scope.securityGroupChoices = {};
        $scope.securityGroupChoicesFullName = {};
        $scope.isRuleExpanded = {};
        $scope.newSecurityGroupName = '';
        $scope.isLoadingSecurityGroup = false;
        $scope.isSecurityGroupsInitialValuesSet = false;
        $scope.role = '';
        $scope.roleList = [];
        $scope.currentStepIndex = 1;
        $scope.step1Invalid = true;
        $scope.step2Invalid = true;
        $scope.step3Invalid = true;
        $scope.imageJsonURL = '';
        $scope.isNotValid = true;
        $scope.existsImage = true;
        $scope.imageIDErrorClass = '';
        $scope.imageIDNonexistErrorClass = '';
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.keyPairChoices = options['keypair_choices'];
            $scope.securityGroupChoices = options['securitygroups_choices'];
            $scope.vpcSubnetList = options['vpc_subnet_choices'];
            $scope.roleList = options['role_choices'];
            $scope.securityGroupJsonEndpoint = options['securitygroups_json_endpoint'];
            $scope.securityGroupsRulesJsonEndpoint = options['securitygroups_rules_json_endpoint'];
            $scope.imageJsonURL = options['image_json_endpoint'];
            $scope.setInitialValues();
            $scope.getAllSecurityGroupsRules();
            $scope.preventFormSubmitOnEnter();
            $scope.initChosenSelectors();
            $scope.watchTags();
            $scope.focusEnterImageID();
            $scope.setWatcher();
        };
        $scope.initChosenSelectors = function () {
            $('#securitygroup').chosen({'width': '100%', search_contains: true});
        };
        $scope.updateSelectedSecurityGroupRules = function () {
            angular.forEach($scope.securityGroups, function(securityGroupID) {
                $scope.selectedGroupRules[securityGroupID] = $scope.securityGroupsRules[securityGroupID];
            });
        };
        $scope.preventFormSubmitOnEnter = function () {
            $(document).ready(function () {
                $('#image-id-input').keydown(function(evt) {
                    if (evt.keyCode === 13) {
                        evt.preventDefault();
                    }
                });
            });
        };
        $scope.setInitialValues = function () {
            $('#number').val($scope.instanceNumber);
            $scope.instanceType = 'm1.small';
            $scope.instanceZone = $('#zone').find(':selected').val();
            var lastVPC = Modernizr.localstorage && localStorage.getItem('lastvpc_inst');
            if (lastVPC != null && $('#vpc_network option[value=' + lastVPC +']').length > 0) {
                $scope.instanceVPC = lastVPC;
            }
            var lastKeyPair = Modernizr.localstorage && localStorage.getItem('lastkeypair_inst');
            if (lastKeyPair != null && $scope.keyPairChoices[lastKeyPair] !== undefined) {
                $('#keypair').val(lastKeyPair);
            }
            $scope.keyPair = $('#keypair').find(':selected').val();
            $scope.imageID = $scope.urlParams['image_id'] || '';
            if( $scope.imageID == '' ){
                $scope.currentStepIndex = 1;
            }else{
                $scope.currentStepIndex = 2;
                $scope.step1Invalid = false;
                $scope.loadImageInfo($scope.imageID);
            }
        };
        $scope.restoreSecurityGroupsInitialValues = function () {
            if ($scope.isSecurityGroupsInitialValuesSet == true) {
                return;
            }
            var lastSecGroup = Modernizr.localstorage && localStorage.getItem('lastsecgroup_inst');
            if (lastSecGroup != null) {
                var lastSecGroupArray = lastSecGroup.split(",");
                angular.forEach(lastSecGroupArray, function (sgroup) {
                    if ($scope.securityGroupChoices[sgroup] !== undefined) {
                        $scope.securityGroups.push(sgroup);
                        $scope.isSecurityGroupsInitialValuesSet = true;
                    }
                });
            }
        };
        $scope.saveOptions = function() {
            if (Modernizr.localstorage) {
                localStorage.setItem('lastvpc_inst', $scope.instanceVPC);
                localStorage.setItem('lastkeypair_inst', $('#keypair').find(':selected').val());
                localStorage.setItem('lastsecgroup_inst', $scope.securityGroups);
            }
        };
        $scope.updateTagsPreview = function () {
            // Need timeout to give the tags time to capture in hidden textarea
            $timeout(function() {
                var tagsTextarea = $('textarea#tags'),
                    tagsJson = tagsTextarea.val(),
                    removeButtons = $('.circle.remove');
                removeButtons.on('click', function () {
                    $scope.updateTagsPreview();
                });
                $scope.tagsObject = JSON.parse(tagsJson);
            }, 300);
        };
        $scope.watchTags = function () {
            var addTagButton = $('#add-tag-btn');
            addTagButton.on('click', function () {
                $scope.updateTagsPreview();
            });
        };
        $scope.checkRequiredInput = function () {
            if( $scope.currentStepIndex == 1 ){ 
                if( $scope.isNotValid == false && $scope.imageID.length < 12 ){
                    // Once invalid ID has been entered, do not enable the button unless the ID length is valid
                    // This prevents the error to be triggered as user is typing for the first time 
                    $scope.isNotValid = true;
                    $scope.imageIDErrorClass = "error";
                }else if( $scope.imageID === '' || $scope.imageID === undefined || $scope.imageID.length == 0 ){
                    // Do not enable the button if the input is empty. However, raise no error message
                    $scope.isNotValid = true;
                    $scope.imageIDErrorClass = "";
                }else if( $scope.imageID.length > 12 ){
                    // If the imageID length is longer then 12, disable the button and raise error message
                    $scope.isNotValid = true;
                    $scope.imageIDErrorClass = "error";
                }else if( $scope.imageID.length >= 4 &&  $scope.imageID.substring(0, 4) != "emi-" && $scope.imageID.substring(0, 4) != "ami-" ){ 
                    // If the imageID length is longer than 4, and they do not consist of "emi-" or "ami-", disable the button and raise error message
                    $scope.isNotValid = true;
                    $scope.imageIDErrorClass = "error";
                }else if( $scope.imageID.length == 12 ){
                    // If the above conditions are met and the image ID length is 12, enable the button
                    $scope.isNotValid = false;
                    $scope.imageIDErrorClass = "";
                }
            }else if( $scope.currentStepIndex == 2 ){
                if( $scope.instanceNumber === '' || $scope.instanceNumber === undefined ){
                    $scope.isNotValid = true;
                }else{
                    $scope.isNotValid = false;
                }
            }else if( $scope.currentStepIndex == 3 ){
                if ($scope.keyPair === '' || $scope.keyPair === undefined) {
                    $scope.isNotValid = true;
                } else if ($scope.securityGroups == undefined || $scope.securityGroups.length == 0) {
                    $scope.isNotValid = true;
                } else {
                    $scope.isNotValid = false;
                }
            }
        };
        $scope.setWatcher = function () {
            $scope.setDialogFocus();
            $scope.$watch('currentStepIndex', function(){
                 $scope.setWizardFocus($scope.currentStepIndex);
            });
            $scope.$watch('imageID', function(newID, oldID){
                // Clear the image ID existence check variables
                $scope.existsImage = true;
                $scope.imageIDNonexistErrorClass = "";
                if (newID != oldID && $scope.imageID.length == 12) {
                    $scope.loadImageInfo(newID);
                }
                $scope.checkRequiredInput();
            });
            $scope.$watch('existsImage', function(newValue, oldValue){
                if( newValue != oldValue &&  $scope.existsImage == false ){
                    $scope.isNotValid = true;
                }
            });
            $scope.$watch('instanceNumber', function(){
                $scope.checkRequiredInput();
            });
            $scope.$watch('keyPair', function(){
                $scope.checkRequiredInput();
            });
            $scope.$watch('securityGroups', function () { 
                $scope.updateSelectedSecurityGroupRules();
                $scope.checkRequiredInput();
            }, true);
            $scope.$watch('securityGroupVPC', function () {
                $scope.$broadcast('updateVPC', $scope.securityGroupVPC);
            });
            $scope.$watch('securityGroupCollection', function () {
                $scope.updateSecurityGroupChoices();
            });
            $scope.$watch('instanceVPC', function () {
                $scope.getInstanceVPCName($scope.instanceVPC);
                $scope.getAllSecurityGroups($scope.instanceVPC);
                $scope.updateVPCSubnetChoices();
            });
            $scope.$watch('instanceZone', function () {
                $scope.updateVPCSubnetChoices();
            });
            $('#number').on('keyup blur', function () {
                var val = $(this).val();
                if (val > 10) {
                    $(this).val(10);
                }
            });
            $scope.$watch('inputtype', function() {
                if ($scope.inputtype == 'text') {
                    $timeout(function() {
                        $('#userdata').focus();
                    });
                }
            });
        };
        $scope.loadImageInfo = function(id) {
            $http({
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                method: 'GET',
                url: $scope.imageJsonURL.replace('_id_', id),
                data: ''
            }).success(function (oData) {
                var item = oData.results;
                $scope.imageName = item.name;
                $scope.imagePlatform = item.platform_name;
                $scope.imageRootDeviceType = item.root_device_type;
                $scope.summarySection.find('.step1').removeClass('hide');
                $scope.$broadcast('setBDM', item.block_device_mapping);
                $scope.existsImage = true;
                $scope.imageIDNonexistErrorClass = "";
                if (item.root_device_type == 'ebs') {
                    // adjust vmtypes menu
                    var rootSize = item.block_device_mapping[item.root_device_name]['size'];
                    var selectedOne = false;
                    angular.forEach($('#instance_type option'), function(value, idx) {
                        var text = value.text;
                        var size = text.split(',')[2].trim();
                        size = size.substring(0, size.indexOf(' '));
                        if (size < rootSize) {  // disable entries that won't fit
                            value.disabled = true;
                        }
                        else {
                            value.disabled = false;
                            if (!selectedOne) {  // select first one that fits
                                value.selected = true;
                                selectedOne = true;
                            }
                        }
                    });
                }
                else {
                    angular.forEach($('#instance_type option'), function(value, idx) {
                        value.disabled = false;
                    });
                }
            }).error(function (oData) {
                $scope.existsImage = false;
                $scope.imageIDNonexistErrorClass = "error";
            });
        };
        $scope.focusEnterImageID = function () {
            // Focus on "Enter Image ID" field if passed appropriate URL param
            if ($scope.urlParams['input_image_id']) {
                $('#image-id-input').focus();
            }
        };
        $scope.setDialogFocus = function () {
            $(document).on('open', '[data-reveal]', function () {
                // When a dialog opens, reset the progress button status
                $(this).find('.dialog-submit-button').css('display', 'block');                
                $(this).find('.dialog-progress-display').css('display', 'none');                
            });
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                modal.find('div.error').removeClass('error');
                var modalID = $(this).attr('id');
                if( modalID.match(/terminate/)  || modalID.match(/delete/) || modalID.match(/release/) ){
                    var closeMark = modal.find('.close-reveal-modal');
                    if(!!closeMark){
                        closeMark.focus();
                    }
                }else{
                    var inputElement = modal.find('input[type!=hidden]').get(0);
                    var modalButton = modal.find('button').get(0);
                    if (!!inputElement && inputElement.value == '') {
                        inputElement.focus();
                    } else if (!!modalButton) {
                        modalButton.focus();
                    }
               }
            });
            $(document).on('submit', '[data-reveal] form', function () {
                // When a dialog is submitted, display the progress button status
                $(this).find('.dialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
            });
            $(document).on('close', '[data-reveal]', function () {
                var modal = $(this);
                modal.find('input[type="text"]').val('');
                modal.find('input:checked').attr('checked', false);
                modal.find('textarea').val('');
                modal.find('div.error').removeClass('error');
                var chosenSelect = modal.find('select');
                if (chosenSelect.length > 0) {
                    chosenSelect.prop('selectedIndex', 0);
                    chosenSelect.chosen();
                }
            });
            $(document).on('closed', '[data-reveal]', function () {
                $scope.setWizardFocus($scope.currentStepIndex);
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
            $scope.launchForm.trigger('validate');
            var currentStep = nextStep - 1,
                tabContent = $scope.launchForm.find('#step' + currentStep),
                invalidFields = tabContent.find('[data-invalid]');
            if (invalidFields.length > 0 || $scope.isNotValid === true) {
                invalidFields.focus();
                $event.preventDefault();
                if( $scope.currentStepIndex > nextStep){
                    $scope.currentStepIndex = nextStep;
                    $scope.checkRequiredInput();
                }
                return false;
            }
            // Handle the unsaved tag issue
            var existsUnsavedTag = false;
            $('input.taginput').each(function(){
                if($(this).val() !== ''){
                    existsUnsavedTag = true;
                }
            });
            if( existsUnsavedTag ){
                $event.preventDefault(); 
                $('#unsaved-tag-warn-modal').foundation('reveal', 'open');
                return false;
            }
            if (nextStep == 2 && $scope.step1Invalid) { $scope.clearErrors(2); $scope.step1Invalid = false; }
            if (nextStep == 3 && $scope.step2Invalid) { $scope.clearErrors(3); $scope.step2Invalid = false; }
            if (nextStep == 4 && $scope.step3Invalid) { $scope.clearErrors(4); $scope.step3Invalid = false; }
            
            // since above lines affects DOM, need to let that take affect first
            $timeout(function() {
                // If all is well, hide current and show new tab without clicking
                // since clicking invokes this method again (via ng-click) and
                // one ng action must complete before another can start
                var hash = "step"+nextStep;
                $("#wizard-tabs").children("dd").each(function() {
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
        $scope.$on('imageSelected', function($event, item) {
            $scope.imageID = item.id;
            $scope.imageName = item.name;
            $scope.imagePlatform = item.platform_name;
            $scope.imageRootDeviceType = item.root_device_type;
            $scope.summarySection.find('.step1').removeClass('hide');
            $scope.checkRequiredInput();
        });
        $scope.buildNumberList = function () {
            // Return a 1-based list of integers of a given size ([1, 2, ... limit])
            var limit = parseInt($scope.instanceNumber, 10) || 10;
            var result = [];
            for (var i = 1; i <= limit; i++) {
                if (limit <= 10) result.push(i);
            }
            return result;
        };
        $scope.showCreateKeypairModal = function() {
            var form = $('#launch-instance-form');
            var invalid_attr = 'data-invalid';
            form.removeAttr(invalid_attr);
            $(invalid_attr, form).removeAttr(invalid_attr);
            $('.error', form).not('small').removeClass('error');
            $scope.keyPairModal.foundation('reveal', 'open');
        };
        $scope.handleKeyPairCreate = function ($event, createUrl, downloadUrl) {
            $event.preventDefault();
            var form = $($event.target);
            if ($scope.newKeyPairName.indexOf('/') !== -1 || $scope.newKeyPairName.indexOf('\\') !== -1) {
                return;
            }
            var formData = form.serialize();
            $scope.isLoadingKeyPair = true;
            $http({
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                method: 'POST',
                url: createUrl,
                data: formData
            }).success(function (oData) {
                $scope.isLoadingKeyPair = false;
                var keypairMaterial = oData['payload'];
                // Add new key pair to choices and set it as selected
                $scope.keyPairChoices[$scope.newKeyPairName] = $scope.newKeyPairName;
                $scope.keyPair = $scope.newKeyPairName;
                Notify.success(oData.message);
                // Download key pair file
                $.generateFile({
                    csrf_token: form.find('input[name="csrf_token"]').val(),
                    filename: $scope.newKeyPairName + '.pem',
                    content: keypairMaterial,
                    script: downloadUrl
                });
                // Close create key pair modal
                var modal = $scope.keyPairModal;
                modal.foundation('reveal', 'close');
                $scope.newKeyPairName = '';
            }).error(function (oData) {
                $scope.isLoadingKeyPair = false;
                eucaHandleError(oData, status);
            });
        };
        $scope.handleSecurityGroupCreate = function ($event, url) {
            $event.preventDefault();
            $scope.isLoadingSecurityGroup = true;
            var formData = $($event.target).serialize();
            $scope.securityGroupForm.trigger('validate');
            if ($scope.securityGroupForm.find('[data-invalid]').length) {
                return false;
            }
            $http({
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                method: 'POST',
                url: url,
                data: formData
            }).success(function (oData) {
                $scope.isLoadingSecurityGroup = false;
                // Add new security group to choices and set it as selected
                var newSecurityGroupID = '';
                if (oData.id) {
                    newSecurityGroupID = oData.id;
                }
                var securityGroupName = $scope.newSecurityGroupName;
                $scope.securityGroupChoicesFullName[newSecurityGroupID] = securityGroupName;
                if (securityGroupName.length > 45) {
                    securityGroupName = securityGroupName.substr(0, 45) + "...";
                }
                $scope.securityGroupChoices[newSecurityGroupID] = securityGroupName;
                $scope.securityGroups.push(newSecurityGroupID);
                var groupRulesObject = JSON.parse($('#rules').val());
                var groupRulesEgressObject = JSON.parse($('#rules_egress').val());
                var groupRulesObjectCombined = groupRulesObject.concat(groupRulesEgressObject); 
                $scope.selectedGroupRules[newSecurityGroupID] = groupRulesObjectCombined; 
                $scope.securityGroupsRules[newSecurityGroupID] = groupRulesObjectCombined;
                // Reset values
                $scope.newSecurityGroupName = '';
                $scope.newSecurityGroupDesc = '';
                $('textarea#rules').val('');
                $('textarea#rules_egress').val('');
                // Timeout is needed for chosen to react after Angular updates the options
                $timeout(function(){
                    $('#securitygroup').trigger('chosen:updated');
                }, 500);
                var modal = $scope.securityGroupModal;
                modal.foundation('reveal', 'close');
                Notify.success(oData.message);
            }).error(function (oData) {
                $scope.isLoadingSecurityGroup = false;
                eucaHandleError(oData, status);
            });
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
        $scope.getAllSecurityGroupsRules = function () {
            var csrf_token = $('#csrf_token').val();
            var data = "csrf_token=" + csrf_token
            $http({
                method:'POST', url:$scope.securityGroupsRulesJsonEndpoint, data:data,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.securityGroupsRules = results;
                $scope.updateSelectedSecurityGroupRules();
            }).error(function (oData) {
                eucaHandleError(oData, status);
            });
        };
        $scope.updateSecurityGroupChoices = function () {
            $scope.securityGroupChoices = {};
            $scope.securityGroupChoicesFullName = {};
            if ($.isEmptyObject($scope.securityGroupCollection)) {
                return;
            }
            $scope.securityGroups = [];
            angular.forEach($scope.securityGroupCollection, function(sGroup){
                var securityGroupName = sGroup['name'];
                $scope.securityGroupChoicesFullName[sGroup['id']] = securityGroupName;
                if (sGroup['name'].length > 45) {
                    securityGroupName = sGroup['name'].substr(0, 45) + "...";
                }
                $scope.securityGroupChoices[sGroup['id']] = securityGroupName;
            }); 
            $scope.restoreSecurityGroupsInitialValues(); 
            // Timeout is needed for chosen to react after Angular updates the options
            $timeout(function(){
                $('#securitygroup').trigger('chosen:updated');
            }, 500);
        };
        $scope.updateVPCSubnetChoices = function () {
            $scope.vpcSubnetChoices = {};
            $scope.subnetVPC = '';
            angular.forEach($scope.vpcSubnetList, function(vpcSubnet){
                if (vpcSubnet['vpc_id'] === $scope.instanceVPC) {
                    if ($scope.instanceZone == '') {
                        $scope.vpcSubnetChoices[vpcSubnet['id']] = 
                            vpcSubnet['cidr_block'] + ' (' + vpcSubnet['id'] + ') | ' + 
                            vpcSubnet['availability_zone'];
                        if ($scope.subnetVPC == '') {
                            $scope.subnetVPC = vpcSubnet['id'];
                        }
                    } else if ($scope.instanceZone != '' && 
                               vpcSubnet['availability_zone'] === $scope.instanceZone) {
                        $scope.vpcSubnetChoices[vpcSubnet['id']] = 
                            vpcSubnet['cidr_block'] + ' (' + vpcSubnet['id'] + ') | ' + 
                            vpcSubnet['availability_zone'];
                        if ($scope.subnetVPC == '') {
                            $scope.subnetVPC = vpcSubnet['id'];
                        }
                    } 
                }
            }); 
            if ($scope.subnetVPC == '') {
                $scope.vpcSubnetChoices['None'] = $('#hidden_vpc_subnet_empty_option').text();
                $scope.subnetVPC = 'None';
            }
        };
        $scope.getInstanceVPCName = function (vpcID) {
            if (vpcID == '') {
                $scope.instanceVPCName = '';
                return;
            }
            var vpcOptions = $('#vpc_network').find('option'); 
            vpcOptions.each(function() {
                if (this.value == vpcID) {
                    $scope.instanceVPCName = this.text;
                } 
            });
        }
    })
;


