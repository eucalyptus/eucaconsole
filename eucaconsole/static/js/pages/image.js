/**
 * @fileOverview Image page JS
 * @requires AngularJS
 *
 */

// Image page includes the tag editor, so pull in that module as well.
angular.module('ImagePage', ['BlockDeviceMappingEditor', 'TagEditor'])
    .controller('ImagePageCtrl', function ($scope, $http, $timeout) {
        $scope.imageState = '';
        $scope.imageStatusEndpoint = '';
        $scope.transitionalStates = ['pending', 'storing'];
        $scope.imageState = '';
        $scope.isPublic = '';
        $scope.errorClass= '';
        $scope.launchPermissions = [];
        $scope.isAccountNotTyped = true;
        $scope.isAccountValid = true;
        $scope.isNotChanged = true;
        $scope.disabledExplanationVisible = false;
        $scope.initController = function (isPublic, launchPermissions, stateUrl){
            $scope.isPublic = isPublic;
            $scope.launchPermissions = launchPermissions;
            $scope.imageStatusEndpoint = stateUrl;
            if (stateUrl) {
                $scope.getImageState();
            }
            $scope.setWatch();
            $scope.setFocus();
        };
        $scope.isTransitional = function (state) {
            return $scope.transitionalStates.indexOf(state) !== -1;
        };
        $scope.setWatch = function () {
            $scope.$on('tagUpdate', function($event) {
                $scope.isNotChanged = false;
            });
            $scope.$watch('isPublic', function(newValue, oldValue) {
                if( newValue !== oldValue ){
                    $scope.isNotChanged = false;
                }
            });
            $scope.$watch('isAccountValid', function() {
                if( $scope.isAccountValid ){
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
                if( $scope.newAccount.length == 12 && $scope.newAccount == parseInt($scope.newAccount) ){
                    $scope.isAccountNotTyped = false;
                    $scope.isAccountValid = true;
                    $scope.$apply();
                }else{
                    if( $scope.newAccount == "" || $scope.newAccount.length == 0 || $scope.newAccount == undefined ){
                        // If new account ID value is null, consider input being cleared, remove the error message
                        $scope.isAccountValid = true;
                    }else if( $scope.newAccount.length > 12 || $scope.newAccount != parseInt($scope.newAccount) ){
                        // If new account ID is longer than 12 chars or contains non-integer, display the error mesage
                        $scope.isAccountValid = false;
                    }else if( $scope.newAccount == parseInt($scope.newAccount) ){
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
                    if($(this).val() !== ''){
                        event.preventDefault(); 
                        $('#unsaved-tag-warn-modal').foundation('reveal', 'open');
                        return false;
                    }
                });
            });
        };
        $scope.getImageState = function () {
            $http.post($scope.imageStatusEndpoint).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $scope.imageState = results['image_status'];
                    // Poll to obtain desired end state if current state is transitional
                    if ($scope.isTransitional($scope.imageState)) {
                        $scope.isUpdating = true;
                        $timeout(function() {$scope.getImageState()}, 4000);  // Poll every 4 seconds
                    } else {
                        if ($scope.isUpdating == true) {
                            // force reload in case image ID got assigned
                            window.location = results.url;
                        }
                        $scope.isUpdating = false;
                    }
                }
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
           if( !$scope.isAccountNotTyped && $scope.isAccountValid ){
               if($scope.hasDup($scope.launchPermissions, $scope.newAccount) != true){
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
               if( thisArray[i] == thisValue ){
                   return true;
               }
           }
           return false;
        };
    })
;

