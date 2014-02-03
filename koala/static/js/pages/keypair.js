/**
 * @fileOverview Keypair Detaile Page JS
 * @requires AngularJS
 *
 */

angular.module('KeypairPage', [])
    .controller('KeypairPageCtrl', function ($scope) {
        $scope.initController = function () {
            $scope.setInitialValues();
            $scope.setWatch();
        };
        $scope.setInitialValues = function () {
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
        };
    })
;



