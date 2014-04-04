/**
 * @fileOverview Launch Config Wizard JS
 * @requires AngularJS
 *
 */

// Launch Config Wizard includes the Image Picker, BDM editor, and security group rules editor
angular.module('LaunchConfigWizard', ['ImagePicker', 'BlockDeviceMappingEditor', 'SecurityGroupRules'])
    .controller('LaunchConfigWizardCtrl', function ($scope, $http) {
        $scope.launchForm = $('#launch-config-form');
        $scope.imageID = '';
        $scope.urlParams = $.url().param();
        $scope.summarySection = $('.summary');
        $scope.instanceTypeSelected = '';
        $scope.securityGroupsRules = {};
        $scope.securityGroupsIDMap = {};
        $scope.keyPairChoices = {};
        $scope.newKeyPairName = '';
        $scope.keyPairSelected = '';
        $scope.keyPairModal = $('#create-keypair-modal');
        $scope.showKeyPairMaterial = false;
        $scope.isLoadingKeyPair = false;
        $scope.securityGroupsRules = {};
        $scope.selectedGroupRules = [];
        $scope.securityGroupModal = $('#create-securitygroup-modal');
        $scope.securityGroupForm = $('#create-securitygroup-form');
        $scope.securityGroupChoices = {};
        $scope.newSecurityGroupName = '';
        $scope.securityGroupSelected = '';
        $scope.isLoadingSecurityGroup = false;
        $scope.currentStepIndex = 1;
        $scope.initController = function (securityGroupsRulesJson, keyPairChoices, securityGroupChoices, securityGroupsIDMapJson) {
            $scope.securityGroupsRules = JSON.parse(securityGroupsRulesJson);
            $scope.keyPairChoices = JSON.parse(keyPairChoices);
            $scope.securityGroupChoices = JSON.parse(securityGroupChoices);
            $scope.securityGroupsIDMap = JSON.parse(securityGroupsIDMapJson);
            $scope.setInitialValues();
            $scope.preventFormSubmitOnEnter();
            $scope.updateSelectedSecurityGroupRules();
            $scope.setWatcher();
            $scope.setFocus();
        };
        $scope.updateSelectedSecurityGroupRules = function () {
            $scope.selectedGroupRules = $scope.securityGroupsRules[$scope.securityGroup];
        };
        $scope.getSecurityGroupIDByName = function (securityGroupName) {
            return $scope.securityGroupsIDMap[securityGroupName];
        };
        $scope.preventFormSubmitOnEnter = function () {
            $(document).ready(function () {
                $(window).keydown(function(evt) {
                    if (evt.keyCode === 13) {
                        evt.preventDefault();
                    }
                });
            });
        };
        $scope.setInitialValues = function () {
            $scope.instanceType = 'm1.small';
            $scope.instanceTypeSelected = $scope.urlParams['instance_type'] || '';
            $scope.instanceNumber = '1';
            $scope.instanceZone = $('#zone').find(':selected').val();
            $scope.keyPair = $('#keypair').find(':selected').val();
            $scope.securityGroup = $('#securitygroup').find(':selected').val();
            $scope.imageID = $scope.urlParams['image_id'] || '';
            $scope.keyPairSelected = $scope.urlParams['keypair'] || '';
            $scope.securityGroupSelected = $scope.urlParams['security_group'] || '';
            if( $scope.instanceTypeSelected != '' )
                $scope.instanceType = $scope.instanceTypeSelected;
            if( $scope.keyPairSelected != '' )
                $scope.keyPair = $scope.keyPairSelected;
            if( $scope.securityGroupSelected != '' )
                $scope.securityGroup = $scope.securityGroupSelected;
            if( $scope.imageID == '' ){
                $scope.currentStepIndex = 1;
            }else{
                $scope.currentStepIndex = 2;
            }
        };
        $scope.setWatcher = function (){
            $scope.$watch('currentStepIndex', function(){
                 $scope.setWizardFocus($scope.currentStepIndex);
            });
            $(document).on('open', '[data-reveal]', function () {
                $(this).find('.dialog-submit-button').css('display', 'block');                
                $(this).find('.dialog-progress-display').css('display', 'none');                
            });
            $(document).on('submit', '[data-reveal] form', function () {
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
                if (chosenSelect.length > 0 && chosenSelect.attr('multiple') == undefined) {
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
                    if (!!inputElement) {
                        inputElement.focus();
                    } else if (!!modalButton) {
                        modalButton.focus();
                    }
               }
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
        $scope.inputImageID = function (url) {
            url += '?image_id=' + $scope.imageID;
            document.location.href = url;
        };
        $scope.visitNextStep = function (nextStep, $event) {
            // Trigger form validation before proceeding to next step
            $scope.launchForm.trigger('validate');
            var currentStep = nextStep - 1,
                tabContent = $scope.launchForm.find('#step' + currentStep),
                invalidFields = tabContent.find('[data-invalid]');
            if (invalidFields.length) {
                invalidFields.focus();
                $event.preventDefault();
                return false;
            }
            // If all is well, click the relevant tab to go to next step
            $('#tabStep' + nextStep).click();
            // Unhide appropriate step in summary
            $scope.summarySection.find('.step' + nextStep).removeClass('hide');
            $scope.currentStepIndex = nextStep;
        };
        $scope.downloadKeyPair = function ($event, downloadUrl) {
            $event.preventDefault();
            var form = $($event.target);
            $.generateFile({
                csrf_token: form.find('input[name="csrf_token"]').val(),
                filename: $scope.newKeyPairName + '.pem',
                content: form.find('textarea[name="content"]').val(),
                script: downloadUrl
            });
            $scope.showKeyPairMaterial = false;
            var modal = $scope.keyPairModal;
            modal.foundation('reveal', 'close');
            $scope.newKeyPairName = '';
        };
        $scope.handleKeyPairCreate = function ($event, url) {
            $event.preventDefault();
            var formData = $($event.target).serialize();
            $scope.isLoadingKeyPair = true;
            $http({
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                method: 'POST',
                url: url,
                data: formData
            }).success(function (oData) {
                $scope.showKeyPairMaterial = true;
                $scope.isLoadingKeyPair = false;
                $('#keypair-material').val(oData['payload']);
                // Add new key pair to choices and set it as selected
                $scope.keyPairChoices[$scope.newKeyPairName] = $scope.newKeyPairName;
                $scope.keyPair = $scope.newKeyPairName;
            }).error(function (oData) {
                $scope.isLoadingKeyPair = false;
                if (oData.message) {
                    Notify.failure(oData.message);
                }
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
                $scope.securityGroupChoices[$scope.newSecurityGroupName] = $scope.newSecurityGroupName;
                $scope.securityGroup = $scope.newSecurityGroupName;
                $scope.selectedGroupRules = JSON.parse($('#rules').val());
                $scope.securityGroupsRules[$scope.newSecurityGroupName] = $scope.selectedGroupRules;
                // Reset values
                $scope.newSecurityGroupName = '';
                $scope.newSecurityGroupDesc = '';
                $('textarea#rules').val('');
                var modal = $scope.securityGroupModal;
                modal.foundation('reveal', 'close');
            }).error(function (oData) {
                $scope.isLoadingSecurityGroup = false;
                if (oData.message) {
                    Notify.failure(oData.message);
                }
            });
        };
    })
;

