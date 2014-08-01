/**
 * @fileOverview Image page JS
 * @requires AngularJS
 *
 */

// Image page includes the tag editor, so pull in that module as well.
angular.module('ImagePage', ['BlockDeviceMappingEditor', 'TagEditor'])
    .controller('ImagePageCtrl', function ($scope) {
        $scope.imageState = '';
        $scope.isPublic = '';
        $scope.errorClass= '';
        $scope.launchPermissions = [];
        $scope.isAccountNotTyped = true;
        $scope.isAccountValid = true;
        $scope.isNotChanged = true;
        $scope.isSubmitted = false;
        $scope.disabledExplanationVisible = false;
        $scope.initController = function (imageState, isPublic, launchPermissions){
            $scope.imageState = imageState;
            $scope.isPublic = isPublic;
            $scope.launchPermissions = launchPermissions;
            $scope.setWatch();
            $scope.setFocus();
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
        $scope.setWatch = function () {
            $scope.$on('tagUpdate', function($event) {
                $scope.isNotChanged = false;
            });
            // Turn "isSubmiited" flag to true when a submit button is clicked on the page
            $('form[id!="euca-logout-form"]').on('submit', function () {
                $scope.isSubmitted = true;
            });
            window.onbeforeunload = function(event) {
                // Conditions to check before navigate away from the page
                // Either by "Submit" or clicking links on the page
                if ($scope.existsUnsavedTag()) {
                    // In case of any unsaved tags, warn the user before unloading the page
                    return $('#warning-message-unsaved-tag').text();
                } else if ($scope.isNotChanged === false) {
                    // No unsaved tags, but some input fields have been modified on the page
                    if ($scope.isSubmitted === true) {
                        // The action is "submit". OK to proceed
                        return;
                    }else{
                        // The action is navigate away.  Warn the user about the unsaved changes
                        return $('#warning-message-unsaved-change').text();
                    }
                }
            };
            // Do not perfom the unsaved changes check if the cancel link is clicked
            $(document).on('click', '.cancel-link', function(event) {
                window.onbeforeunload = null;
            });
            // Handle the case when user tries to open a dialog while there exist unsaved changes
            $(document).on('open', '[data-reveal][id!="unsaved-changes-warning-modal"][id!="unsaved-tag-warn-modal"]', function () {
                // If there exist unsaved changes
                if ($scope.existsUnsavedTag() || $scope.isNotChanged === false) {
                    var self = this;
                    // Close the current dialog as soon as it opens
                    $(self).on('opened', function() {
                        $(self).off('opened');
                        $(self).foundation('reveal', 'close');
                    });
                    // Open the warning message dialog instead
                    $(self).on('closed', function() {
                        $(self).off('closed');
                        var modal = $('#unsaved-changes-warning-modal');
                        modal.foundation('reveal', 'open');
                    });
                } 
            });
            $scope.$watch('isPublic', function(newValue, oldValue) {
                if (newValue !== oldValue) {
                    $scope.isNotChanged = false;
                }
            });
            $scope.$watch('isAccountValid', function() {
                if ($scope.isAccountValid) {
                    $scope.errorClass = '';
                }else{
                    $scope.errorClass= 'error';
                }
            });
            $(document).on('input', '#description', function () {
                $scope.isNotChanged = false;
                $scope.$apply();
            });
            $(document).on('keyup', '#add-account-inputbox', function () {
                // New account ID needs to be 12 chars and contains only integers
                if ($scope.newAccount.length == 12 && $scope.newAccount == parseInt($scope.newAccount)) {
                    $scope.isAccountNotTyped = false;
                    $scope.isAccountValid = true;
                    $scope.$apply();
                }else{
                    if ($scope.newAccount == "" || $scope.newAccount.length == 0 || $scope.newAccount == undefined) {
                        // If new account ID value is null, consider input being cleared, remove the error message
                        $scope.isAccountValid = true;
                    } else if ($scope.newAccount.length > 12 || $scope.newAccount != parseInt($scope.newAccount)) {
                        // If new account ID is longer than 12 chars or contains non-integer, display the error mesage
                        $scope.isAccountValid = false;
                    } else if ($scope.newAccount == parseInt($scope.newAccount)) {
                        // If new account ID value contains only integers, remove the error message
                        $scope.isAccountValid = true;
                    }
                    // Indicate a value has been entered into the account ID inputbox
                    $scope.isAccountNotTyped = true;
                    $scope.$apply();
                }
            });
            // Handle the unsaved tag issue
            $(document).on('submit', '#image-detail-form', function(event) {
                $('input.taginput').each(function(){
                    if ($(this).val() !== '') {
                        event.preventDefault(); 
                        $('#unsaved-tag-warn-modal').foundation('reveal', 'open');
                        return false;
                    }
                });
            });
        };
        $scope.setFocus = function () {
            $(document).on('ready', function(){
                $('.actions-menu').find('a').get(0).focus();
            });
        };
        $scope.removeAccount = function (account) {
            var index = $scope.launchPermissions.indexOf(account);
            if (index > -1) {
                $scope.launchPermissions.splice(index, 1);
            }        
            $scope.isNotChanged = false;
            $scope.$apply();
        };
        $scope.addAccount = function () {
           if (!$scope.isAccountNotTyped && $scope.isAccountValid) {
               if ($scope.hasDup($scope.launchPermissions, $scope.newAccount) != true) {
                   $scope.launchPermissions.push($scope.newAccount);
               }
               $scope.newAccount = "";
               $scope.isAccountNotTyped = true;
               $scope.isAccountValid = true;
               $scope.isNotChanged = false;
           } 
        };
        $scope.hasDup = function(thisArray, thisValue){
           for( var i = 0; i < thisArray.length; i++ ){
               if (thisArray[i] == thisValue) {
                   return true;
               }
           }
           return false;
        };
    })
;

