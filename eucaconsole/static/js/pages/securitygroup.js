/**
 * @fileOverview SecurityGroup Detail Page JS
 * @requires AngularJS
 *
 */

angular.module('SecurityGroupPage', ['TagEditor', 'SecurityGroupRules'])
    .controller('SecurityGroupPageCtrl', function ($scope) {
        $scope.isNotChanged = true;
        $scope.initController = function () {
            $scope.setWatch();
            $scope.setFocus();
        };
        $scope.setWatch = function () {
            // Handle the unsaved tag issue
            $(document).on('submit', '#security-group-detail-form', function(event) {
                $('input.taginput').each(function(){
                    if($(this).val() !== ''){
                        event.preventDefault(); 
                        $('#unsaved-tag-warn-modal').foundation('reveal', 'open');
                        return false;
                    }
                });
            });
            window.addEventListener("beforeunload", function(event) {
                var existsUnsavedTag = false;
                $('input.taginput').each(function(){
                    if($(this).val() !== ''){
                        existsUnsavedTag = true;
                    }
                });
                if(existsUnsavedTag){
                    return "You must click the \"Add\" button before you submit this for your tag to be included.";
                }else if($scope.isNotChanged === false){
                    if( event.target.activeElement.id === 'save-securitygroup-btn' ){ 
                        return;
                    }
                    return "You must click the \"Save Changes\" button before you leave this page.";
                }
            });
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
            });
        };
        $scope.setFocus = function () {
            $scope.$on('tagUpdate', function($event) {
                $scope.isNotChanged = false;
            });
            $scope.$on('securityGroupUpdate', function($event) {
                $scope.isNotChanged = false;
            });
            $(document).on('ready', function(){
                if( $('.actions-menu').length > 0 ){
                    $('.actions-menu').find('a').get(0).focus();
                }
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



