/**
 * @fileOverview S3 Sharing Panel JS
 * @requires AngularJS
 *
 */
angular.module('S3SharingPanel', [])
    .controller('S3SharingPanelCtrl', function ($scope) {
        $scope.s3AclTextarea = $('#s3-sharing-panel');
        $scope.sharingAccountList = [];
        $scope.isNotValid = true;
        $scope.initS3SharingPanel = function () {

        };
    })
;
