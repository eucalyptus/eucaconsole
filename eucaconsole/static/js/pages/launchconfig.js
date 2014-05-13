/**
 * @fileOverview LaunchConfig Detail Page JS
 * @requires AngularJS
 *
 */

angular.module('LaunchConfigPage', ['BlockDeviceMappingEditor'])
    .controller('LaunchConfigPageCtrl', function ($scope) {
        $scope.initController = function (inUse, image) {
            $scope.launchConfigInUse = inUse;
            $scope.setWatch();
            $scope.setFocus();
            if (image == '') {
                $('#image-missing-modal').foundation('reveal', 'open');
            }
        };
        $scope.setWatch = function () {
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
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



