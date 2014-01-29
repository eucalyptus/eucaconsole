/**
 * @fileOverview Launch Config Wizard JS
 * @requires AngularJS
 *
 */

// Launch Config Wizard includes the Image Picker, and the Block Device Mapping editor
angular.module('LaunchConfigWizard', ['ImagePicker', 'BlockDeviceMappingEditor'])
    .controller('LaunchConfigWizardCtrl', function ($scope, $timeout) {
        $scope.form = $('#launch-config-form');
        $scope.imageID = '';
        $scope.urlParams = $.url().param();
        $scope.summarySection = $('.summary');
        $scope.securityGroupsRules = {};
        $scope.selectedGroupRules = [];
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
        $scope.initController = function (securityGroupsRulesJson) {
            $scope.setInitialValues();
            $scope.securityGroupsRules = JSON.parse(securityGroupsRulesJson);
            $scope.updateSelectedSecurityGroupRules();
        };
        $scope.inputImageID = function (url) {
            url += '?image_id=' + $scope.imageID;
            document.location.href = url;
        };
        $scope.visitNextStep = function (nextStep, $event) {
            // Trigger form validation before proceeding to next step
            $scope.form.trigger('validate');
            var currentStep = nextStep - 1,
                tabContent = $scope.form.find('#step' + currentStep),
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
    })
;

