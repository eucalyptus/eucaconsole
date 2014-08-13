/**
 * @fileOverview IAM Create Account Page JS
 * @requires AngularJS
 *
 */

angular.module('AccountPage', [])
    .controller('AccountPageCtrl', function ($scope, $timeout) {
        $scope.accountName = '';
        $scope.isNotValid = true;
        $scope.initController = function () {
            $scope.setWatch();
        };
        $scope.setWatch = function () {
            $scope.$watch('accountName' , function () {
                if( $scope.accountName === '' || $scope.accountName === undefined ){
                    $scope.isNotValid = true;
                }else{
                    $scope.isNotValid = false;
                }
            });
        };
    })
;



