/**
 * @fileOverview Security Group Page JS
 * @requires AngularJS
 *
 */

angular.module('SecurityGroupPage', ['TagEditor', 'SecurityGroupRules'])
    .controller('SecurityGroupPageCtrl', function ($scope) {
        $scope.isHelpExpanded = false;
        $scope.toggleHelpContent = function () {
            $scope.isHelpExpanded = !$scope.isHelpExpanded;
        };
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



