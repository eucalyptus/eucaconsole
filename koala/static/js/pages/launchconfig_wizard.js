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
        $scope.securityGroupsRules = {};
        $scope.keyPairChoices = {};
        $scope.newKeyPairName = '';
        $scope.keyPairModal = $('#create-keypair-modal');
        $scope.showKeyPairMaterial = false;
        $scope.isLoadingKeyPair = false;
        $scope.securityGroupsRules = {};
        $scope.selectedGroupRules = [];
        $scope.securityGroupModal = $('#create-securitygroup-modal');
        $scope.securityGroupForm = $('#create-securitygroup-form');
        $scope.securityGroupChoices = {};
        $scope.newSecurityGroupName = '';
        $scope.isLoadingSecurityGroup = false;
        $scope.updateSelectedSecurityGroupRules = function () {
            $scope.selectedGroupRules = $scope.securityGroupsRules[$scope.securityGroup];
        };
        $scope.setInitialValues = function () {
            $scope.instanceType = $scope.urlParams['instance_type'] || 'm1.small';
            $scope.instanceNumber = '1';
            $scope.instanceZone = $('#zone').find(':selected').val();
            $scope.keyPair = $('#keypair').find(':selected').val();
            $scope.securityGroup = $('#securitygroup').find(':selected').val();
            $scope.imageID = $scope.urlParams['image_id'] || '';
        };
        $scope.initController = function (securityGroupsRulesJson, keyPairChoices, securityGroupChoices) {
            $scope.setInitialValues();
            $scope.setFocus();
            $scope.securityGroupsRules = JSON.parse(securityGroupsRulesJson);
            $scope.updateSelectedSecurityGroupRules();
            $scope.keyPairChoices = JSON.parse(keyPairChoices);
            $scope.securityGroupChoices = JSON.parse(securityGroupChoices);
        };
        $scope.setFocus = function () {
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var inputElement = modal.find('input[type!=hidden]').get(0);
                if( inputElement != undefined ){
                    inputElement.focus()
                }else{
                    modal.find('button').get(0).focus();
                }
            });
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
                    alert(oData.message);
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
                    alert(oData.message);
                }
            });
        };
    })
;

