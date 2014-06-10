/**
 * @fileOverview Image page JS
 * @requires AngularJS
 *
 */

// Image page includes the tag editor, so pull in that module as well.
angular.module('ImagePage', ['TagEditor'])
    .controller('ImagePageCtrl', function ($scope) {
        $scope.isNotChanged = true;
        $scope.initController = function (){
            $scope.setWatch();
            $scope.setFocus();
        };
        $scope.setWatch = function () {
            $scope.$on('tagUpdate', function($event) {
                $scope.isNotChanged = false;
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
                }
            });
        };
        $scope.setFocus = function () {
            $(document).on('ready', function(){
                $('.actions-menu').find('a').get(0).focus();
            });
        };
    })
;

