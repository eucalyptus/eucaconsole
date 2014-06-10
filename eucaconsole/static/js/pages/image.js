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
        };
        $scope.setFocus = function () {
            $(document).on('ready', function(){
                $('.actions-menu').find('a').get(0).focus();
            });
        };
    })
;

