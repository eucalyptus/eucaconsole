/**
 * @fileOverview Image Detaile Page JS
 * @requires AngularJS
 *
 */

angular.module('ImagePage', ['TagEditor'])
    .controller('ImagePageCtrl', function ($scope) {
        $scope.initController = function () {
            $scope.setInitialValues();
            $scope.setWatch();
        };
        $scope.setInitialValues = function () {
        };
        $scope.setWatch = function () {
        };
    })
;



