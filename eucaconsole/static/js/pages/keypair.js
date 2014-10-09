/**
 * @fileOverview Keypair Detaile Page JS
 * @requires AngularJS
 *
 */

angular.module('KeypairPage', ['EucaConsoleUtils'])
    .controller('KeypairPageCtrl', function ($scope, eucaUnescapeJson) {
        $scope.keypairName = '';
        $scope.keypairMaterial = '';
        $scope.isNotValid = true;
        $scope.routeID = '';
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.routeID = options['route_id'];
            $scope.setWatch();
            $scope.setFocus();
        };
        $scope.checkRequiredInput = function () {
            $scope.isNotValid = $scope.keypairName === '' || $scope.keypairName === undefined;
            // Extra check for Import Keypair case
            if ($scope.routeID === 'new2') {
                $scope.isNotValid = $scope.keypairMaterial === '' || $scope.keypairMaterial === undefined;
            }
        };
        $scope.setWatch = function () {
            // JAVASCRIPT SNIPPET TAKEN FROM 3.4.1 TO ADD A LISTENER TO THE FILE UPLOAD INPUTBOX
            $('#key-import-file').on('change', function(evt) {
                var file = evt.target.files[0];
                var reader = new FileReader();
                reader.onloadend = function(evt) {
                    if (evt.target.readyState == FileReader.DONE) {
                        $('#key-import-contents').val(evt.target.result).trigger('keyup');
                        $scope.keypairMaterial = evt.target.result;
                        $scope.$apply();
                    }
                }
                reader.readAsText(file);
            });
            $scope.$watch('keypairName', function () {
                $scope.checkRequiredInput();
            });
            $scope.$watch('keypairMaterial', function () {
                $scope.checkRequiredInput();
            });
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
            });
        };
        $scope.setFocus = function () {
            $(document).on('ready', function(){
                var firstLink = $('.actions-menu').find('a');
                if( firstLink.length > 0 ){
                    firstLink.get(0).focus();
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



