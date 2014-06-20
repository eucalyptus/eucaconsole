/**
 * @fileOverview IAM Create Group Page JS
 * @requires AngularJS
 *
 */

angular.module('GroupPage', [])
    .controller('GroupPageCtrl', function ($scope, $timeout) {
        $scope.groupName = '';
        $scope.isNotValid = true;
        $scope.initController = function (group_users, all_users) {
            $scope.setWatch();
        };
        $scope.setWatch = function () {
            $scope.$watch('groupName' , function () {
                if( $scope.groupName === '' || $scope.groupName === undefined ){
                    $scope.isNotValid = true;
                }else{
                    $scope.isNotValid = false;
                }
            });
        };
    })
;



