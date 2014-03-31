/**
 * @fileOverview Keypair Detaile Page JS
 * @requires AngularJS
 *
 */

angular.module('KeypairPage', [])
    .controller('KeypairPageCtrl', function ($scope) {
        $scope.initController = function () {
            $scope.setWatch();
            $scope.setFocus();
        };
        $scope.setWatch = function () {
            // JAVASCRIPT SNIPPET TAKEN FROM 3.4.1 TO ADD A LISTENER TO THE FILE UPLOAD INPUTBOX
            $('#key-import-file').on('change', function(evt) {
                var file = evt.target.files[0];
                var reader = new FileReader();
                reader.onloadend = function(evt) {
                    if (evt.target.readyState == FileReader.DONE) {
                        $('#key-import-contents').val(evt.target.result).trigger('keyup');
                    }
                }
                reader.readAsText(file);
            });
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
            });
        };
        $scope.setFocus = function () {
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



