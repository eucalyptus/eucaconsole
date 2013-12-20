/**
 * @fileOverview Launch Instance page JS
 * @requires AngularJS
 *
 */

// Launch Instance page includes the tag editor and Block Device Mapping editor, so pull in those modules
angular.module('LaunchInstance', ['TagEditor', 'BlockDeviceMappingEditor'])
    .controller('LaunchInstanceCtrl', function ($scope, $timeout) {
        $scope.form = $('#launch-instance-form');
        $scope.tagsObject = {};
        $scope.urlParams = $.url().param();
        $scope.setInitialValues = function () {
            $scope.instanceType = 'm1.small';
            $scope.instanceNumber = '1';
            $scope.instanceZone = $('#zone').find(':selected').val();
            $scope.keyPair = $('#keypair').find(':selected').val();
            $scope.securityGroup = $('#securitygroup').find(':selected').val();
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
        $scope.initController = function () {
            $scope.setInitialValues();
            $scope.watchTags();
            $scope.focusEnterImageID();
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
    })
;

