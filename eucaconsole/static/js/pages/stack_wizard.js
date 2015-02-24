/**
 * @fileOverview Stack wizard page JS
 * @requires AngularJS
 *
 */

// Launch Instance page includes the Tag Editor, the Image Picker, BDM editor, and security group rules editor
angular.module('StackWizard', ['TagEditor', 'EucaConsoleUtils'])
    .controller('StackWizardCtrl', function ($scope, $http, $timeout, eucaHandleError, eucaUnescapeJson) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.tagsObject = {};
        $scope.summarySection = $('.summary');
        $scope.currentStepIndex = 1;
        $scope.step1Invalid = true;
        $scope.step2Invalid = true;
        $scope.imageJsonURL = '';
        $scope.isNotValid = true;
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.setInitialValues();
            $scope.initChosenSelectors();
            $scope.watchTags();
            $scope.setWatcher();
        };
        $scope.initChosenSelectors = function () {
            $('sample-template').chosen({'width': '100%', search_contains: true});
        };
        $scope.setInitialValues = function () {
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
            if ($scope.currentStepIndex == 1) { 
                if ($scope.isNotValid === false && $scope.stackName.length < 256) {
                    // Once invalid name has been entered, do not enable the button unless the name length is valid
                    $scope.isNotValid = true;
                }
            } else if ($scope.currentStepIndex == 2) {
                $scope.isNotValid = false;
            }
        };
        $scope.setWatcher = function () {
            $scope.$watch('currentStepIndex', function(){
                 $scope.setWizardFocus($scope.currentStepIndex);
            });
            $scope.$watch('inputtype', function() {
                if ($scope.inputType == 'text') {
                    $timeout(function() {
                        $('#sample-template').focus();
                    });
                }
                else {
                    if ($scope.inputType == 'url') {
                        $timeout(function() {
                            $('#template-url').focus();
                        });
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
            
            // since above lines affects DOM, need to let that take affect first
            $timeout(function() {
                // If all is well, hide current and show new tab without clicking
                // since clicking invokes this method again (via ng-click) and
                // one ng action must complete before another can start
                var hash = "step"+nextStep;
                $("#wizard-tabs").children("dd").each(function() {
                    var link = $(this).find("a");
                    if (link.length !== 0) {
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
    })
;


