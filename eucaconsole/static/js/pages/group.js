/**
 * @fileOverview IAM Group Detaile Page JS
 * @requires AngularJS
 *
 */

angular.module('GroupPage', ['PolicyList'])
    .controller('GroupPageCtrl', function ($scope, $timeout) {
        $scope.groupUsers = [];
        $scope.allUsers = [];
        $scope.isSubmitted = false;
        $scope.isNotChanged = true;
        $scope.pendingModalID = '';
        $scope.initController = function (group_users, all_users) {
            $scope.groupUsers = group_users;
            $scope.allUsers = all_users;
            $scope.setWatch();
            $scope.setFocus();
            $timeout(function(){ $scope.activateChosen(); }, 100);
        };
        $scope.activateChosen = function () {
            $("#users-select").chosen();
            $("#users_select_chosen .chosen-choices").bind("DOMSubtreeModified", function(e) {
                $timeout(function(){ $scope.adjustGroupUsers(); }, 100);
            });
        };
        $scope.adjustGroupUsers = function () {
            var newUsers = [];
            $("#users_select_chosen .chosen-choices .search-choice").each(function (index){
                var thisUser = $( this ).text();
                newUsers.push(thisUser);
            });
            var userAdded = false;
            if( $scope.groupUsers.length < newUsers.length ){
                userAdded = true;
            }
            $scope.groupUsers = newUsers;
            if( userAdded == true ){
                $scope.isNotChanged = false;
                $scope.$apply();
            }
        };
        $scope.removeUser = function (user) {
            $("#users_select_chosen .chosen-choices .search-choice").each(function (index){
                var thisUser = $( this ).text();
                if( thisUser == user ){
                    $( this ).children('a').click();
                    $scope.isNotChanged = false;
                    $scope.$apply();
                }
            });
        };
        $scope.isSelected = function (user) {
            for (i in $scope.groupUsers){
                if( user == $scope.groupUsers[i] ){
                   return true;
                }
            }
           return false;
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
                if ($scope.isNotChanged === false) {
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
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
            });
            $(document).on('input', 'input[type="text"]', function () {
                $scope.isNotChanged = false;
                $scope.$apply();
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
                }else if ($scope.isNotChanged === false) {
                    // Warn the user about the unsaved changes
                    return $('#warning-message-unsaved-changes').text();
                }
                return;
            };
            // Do not perfom the unsaved changes check if the cancel link is clicked
            $(document).on('click', '.cancel-link', function(event) {
                window.onbeforeunload = null;
            });
        };
        $scope.setFocus = function () {
            $(document).on('ready', function(){
                $('.actions-menu').find('a').get(0).focus();
            });
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
    })
;



