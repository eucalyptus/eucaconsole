/**
 * @fileOverview New user page JS
 * @requires AngularJS
 *
 */

// New user page includes the User Editor editor
angular.module('UserNew', ['UserEditor'])
    .controller('UserNewCtrl', function ($scope) {
        $scope.form = $('#user-new-form');
        $scope.quotas_expanded = false;
        $scope.adv_expanded = false;
        $scope.ec2_expanded = false;
        $scope.s3_expanded = false;
        $scope.autoscale_expanded = false;
        $scope.elb_expanded = false;
        $scope.iam_expanded = false;
        $scope.toggleQuotasContent = function () {
            $scope.quotas_expanded = !$scope.quotas_expanded;
        };
        $scope.toggleAdvContent = function () {
            $scope.adv_expanded = !$scope.adv_expanded;
        };
        $scope.toggleEC2Content = function () {
            $scope.ec2_expanded = !$scope.ec2_expanded;
        };
        $scope.toggleS3Content = function () {
            $scope.s3_expanded = !$scope.s3_expanded;
        };
        $scope.toggleAutoscaleContent = function () {
            $scope.autoscale_expanded = !$scope.autoscale_expanded;
        };
        $scope.toggleELBContent = function () {
            $scope.elb_expanded = !$scope.elb_expanded;
        };
        $scope.toggleIAMContent = function () {
            $scope.iam_expanded = !$scope.iam_expanded;
        };
    })
;

