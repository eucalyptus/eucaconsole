/**
 * @fileOverview Launch Instance page JS
 * @requires AngularJS
 *
 */

// Launch Instance page includes the Tag Editor, the Image Picker, and the Block Device Mapping editor
angular.module('LaunchInstance', ['TagEditor', 'BlockDeviceMappingEditor', 'ImagePicker', 'SecurityGroupRules'])
    .controller('LaunchInstanceCtrl', function ($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.form = $('#launch-instance-form');
        $scope.tagsObject = {};
        $scope.imageID = '';
        $scope.urlParams = $.url().param();
        $scope.instanceNumber = 1;
        $scope.instanceNames = [];
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
            $('#number').val($scope.instanceNumber);
            $scope.instanceType = 'm1.small';
            $scope.instanceZone = $('#zone').find(':selected').val();
            $scope.keyPair = $('#keypair').find(':selected').val();
            $scope.securityGroup = $('#securitygroup').find(':selected').val();
            $scope.imageID = $scope.urlParams['image_id'] || '';
        };
        $scope.updateTagsPreview = function () {
            // Need timeout to give the tags time to capture in hidden textarea
            $timeout(function() {
                var tagsTextarea = $('#tags'),
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
        $scope.focusEnterImageID = function () {
            // Focus on "Enter Image ID" field if passed appropriate URL param
            if ($scope.urlParams['input_image_id']) {
                $('#image-id-input').focus();
            }
        };
        $scope.inputImageID = function (url) {
            url += '?image_id=' + $scope.imageID;
            document.location.href = url;
        };
        $scope.initController = function (securityGroupsRulesJson, keyPairChoices, securityGroupChoices) {
            $scope.securityGroupsRules = JSON.parse(securityGroupsRulesJson);
            $scope.setInitialValues();
            $scope.updateSelectedSecurityGroupRules();
            $scope.watchTags();
            $scope.focusEnterImageID();
            $scope.keyPairChoices = JSON.parse(keyPairChoices);
            $scope.securityGroupChoices = JSON.parse(securityGroupChoices);
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
        };
        $scope.buildNumberList = function (limit) {
            // Return a 1-based list of integers of a given size ([1, 2, ... limit])
            limit = parseInt(limit, 10);
            var result = [];
            for (var i = 1; i <= limit; i++) {
                result.push(i);
            }
            return result;
        };
        $scope.confirmKeyPair = function ($event) {
            $event.preventDefault();
            $scope.showKeyPairMaterial = false;
            $scope.keyPairModal.foundation('reveal', 'close');
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
                $scope.newKeyPairName = '';
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
                $('textarea#tags').val('');
                $scope.securityGroupModal.foundation('reveal', 'close');
            }).error(function (oData) {
                $scope.isLoadingSecurityGroup = false;
                if (oData.message) {
                    alert(oData.message);
                }
            });
        };
    })
;

