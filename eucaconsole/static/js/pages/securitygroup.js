/**
 * @fileOverview SecurityGroup Detail Page JS
 * @requires AngularJS
 *
 */

angular.module('SecurityGroupPage', ['TagEditor', 'SecurityGroupRules','EucaConsoleUtils'])
    .controller('SecurityGroupPageCtrl', function ($scope, eucaUnescapeJson) {
        $scope.isNotValid = true;
        $scope.isNotChanged = true;
        $scope.isSubmitted = false;
        $scope.securityGroupName = undefined;
        $scope.securityGroupDescription = undefined;
        $scope.securityGroupVPC = undefined;
        $scope.invalidRulesArray = [];
        $scope.invalidRulesEgressArray = [];
        $scope.pendingModalID = '';
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.securityGroupVPC = options['default_vpc_network'];
            $scope.setWatch();
            $scope.setFocus();
        };
        $scope.checkRequiredInput = function () {
            if ($scope.securityGroupName === undefined || $scope.securityGroupDescription === undefined) {
               $scope.isNotValid = true;
            } else {
               $scope.isNotValid = false;
            }
        };
        // True if there exists an unsaved key or value in the tag editor field
        $scope.existsUnsavedTag = function () {
            var hasUnsavedTag = false;
            $('input.taginput[type!="checkbox"]').each(function(){
                if ($(this).val() !== '') {
                    hasUnsavedTag = true;
                }
            });
            return hasUnsavedTag;
        };
        $scope.openModalById = function (modalID) {
            var modal = $('#' + modalID);
            modal.foundation('reveal', 'open');
            modal.find('h3').click();  // Workaround for dropdown menu not closing
            // Clear the pending modal ID if opened
            if ($scope.pendingModalID === modalID) {
                $scope.pendingModalID = '';
            }
        };
        $scope.setWatch = function () {
            // Monitor the action menu click
            $(document).on('click', 'a[id$="action"]', function (event) {
                // Ingore the action if the link has ng-click or href attribute defined
                if (this.getAttribute('ng-click')) {
                    return;
                } else if (this.getAttribute('href') && this.getAttribute('href') !== '#') {
                    return;
                }
                // the ID of the action link needs to match the modal name
                var modalID = this.getAttribute('id').replace("-action", "-modal");
                // If there exists unsaved changes, open the wanring modal instead
                if ($scope.existsUnsavedTag() || $scope.isNotChanged === false ||
                    $('#add-rule-button-div').hasClass('ng-hide') === false) {
                    $scope.pendingModalID = modalID;
                    $scope.openModalById('unsaved-changes-warning-modal');
                    return;
                } 
                $scope.openModalById(modalID);
            });
            // Leave button is clicked on the warning unsaved changes modal
            $(document).on('click', '#unsaved-changes-warning-modal-stay-button', function () {
                $('#unsaved-changes-warning-modal').foundation('reveal', 'close');
            });
            // Stay button is clicked on the warning unsaved changes modal
            $(document).on('click', '#unsaved-changes-warning-modal-leave-link', function () {
                $scope.openModalById($scope.pendingModalID);
            });
            // Close button is clicked on the invalid rules warning modal
            $(document).on('click', '#invalid-rules-warning-close-button', function () {
                $('#invalid-rules-warning-modal').foundation('reveal', 'close');
            });
            $scope.$watch('securityGroupName', function () {
                $scope.checkRequiredInput(); 
            });
            $scope.$watch('securityGroupDescription', function () {
                $scope.checkRequiredInput();
            });
            $scope.$watch('securityGroupVPC', function () {
                $scope.$broadcast('updateVPC', $scope.securityGroupVPC);
                $scope.checkRequiredInput(); 
            });
            // Handle the unsaved tag issue
            $(document).on('submit', '#security-group-detail-form', function(event) {
                // Handle the unsaved security group rule issue
                if ($('#add-rule-button-div').hasClass('ng-hide') === false) {
                        event.preventDefault(); 
                        $scope.isSubmitted = false;
                        $('#unsaved-rule-warn-modal').foundation('reveal', 'open');
                        return false;
                }
                $('input.taginput').each(function(){
                    if ($(this).val() !== '') {
                        event.preventDefault(); 
                        $scope.isSubmitted = false;
                        $('#unsaved-tag-warn-modal').foundation('reveal', 'open');
                        return false;
                    }
                });
            });
            // Turn "isSubmiited" flag to true when a submit button is clicked on the page
            $('form[id!="euca-logout-form"]').on('submit', function () {
                $scope.isSubmitted = true;
            });
            // Conditions to check before navigate away
            window.onbeforeunload = function(event) {
                if ($scope.isSubmitted === true) {
                   // The action is "submit". OK to proceed
                   return;
                }else if ($scope.existsUnsavedTag() || $scope.isNotChanged === false || 
                    $('#add-rule-button-div').hasClass('ng-hide') === false) {
                    // Warn the user about the unsaved changes
                    return $('#warning-message-unsaved-changes').text();
                }
            };
            // Do not perfom the unsaved changes check if the cancel link is clicked
            $(document).on('click', '.cancel-link', function(event) {
                window.onbeforeunload = null;
            });
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.gialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
            });
            // Listen for the events broadcast
            $scope.$on('tagUpdate', function($event) {
                $scope.isNotChanged = false;
            });
            $scope.$on('securityGroupUpdate', function($event) {
                $scope.isNotChanged = false;
            });
            $scope.$on('invalidRulesWarning', function($event, invalidRules, invalidRulesEgress) {
                $scope.invalidRulesArray = invalidRules;
                $scope.invalidRulesEgressArray = invalidRulesEgress;
                $('#invalid-rules-warning-modal').foundation('reveal', 'open');
            });
        };
        $scope.setFocus = function () {
            $(document).on('ready', function(){
                var firstLink = $('.actions-menu').find('a');
                if (firstLink.length > 0) {
                    firstLink.get(0).focus();
                }
            });
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var modalID = $(this).attr('id');
                if (modalID.match(/terminate/) || modalID.match(/delete/) || modalID.match(/release/)) {
                    var closeMark = modal.find('.close-reveal-modal');
                    if (!!closeMark) {
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
    })
;



