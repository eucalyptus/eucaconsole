/**
 * @fileOverview New user page JS
 * @requires AngularJS
 *
 */

// New user page includes the User Editor editor
angular.module('UserNew', ['UserEditor'])
    .controller('UserNewCtrl', function ($scope) {
        $scope.form = $('#user-new-form');
        $scope.submitEndpoint = '';
        $scope.allUsersRedirect = '';
        $scope.singleUserRedirect = '';
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
        $scope.initController = function(submitEndpoint, allRedirect, singleRedirect) {
            $scope.submitEndpoint = submitEndpoint
            $scope.allUsersRedirect = allRedirect
            $scope.singleUserRedirect = singleRedirect
        }
        $scope.submit = function($event) {
            var form = $($event.target);
            var singleUser = JSON.parse(form.find('textarea[name="users"]').val())
            singleUser = Object.keys(singleUser).length == 1;
            var data = $($event.target).serialize();
            $.generateFile({
                csrf_token: form.find('input[name="csrf_token"]').val(),
                filename: "not-used", // let the server set this
                content: data,
                script: $scope.submitEndpoint
            });
            // this is clearly a hack. We'd need to bake callbacks into the generateFile
            // stuff to do this properly. Probably should open an issue. TODO
            /* this won't work properly unless we have a big delay, or proper callbacks
            setTimeout(function() {
                if (!singleUser) {
                    window.location = $scope.allUsersRedirect;
                } else {
                    window.location = $scope.singleUserRedirect;
                }
            }, 5000);
            */
        };
    })
;

