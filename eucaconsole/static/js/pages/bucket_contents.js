/**
 * @fileOverview Bucket detail (contents) page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('BucketContentsPage', ['LandingPage'])
    .controller('BucketContentsCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketName = '';
        $scope.deletingAll = false;
        $scope.initController = function () {
        };
        $scope.revealModal = function (action, bucket) {
            var modal = $('#' + action + '-bucket-modal');
            $scope.bucketName = bucket['name'];
            modal.foundation('reveal', 'open');
        };
        $scope.deleteAll = function () {
            $scope.deletingAll = true;
        };
    })
;

