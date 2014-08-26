/**
 * @fileOverview Bucket detail (contents) page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('BucketViewPage', ['LandingPage'])
    .controller('BucketViewCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketName = '';
        $scope.initController = function () {
        };
        $scope.revealModal = function (action, bucket) {
            var modal = $('#' + action + '-bucket-modal');
            $scope.bucketName = bucket['name'];
            modal.foundation('reveal', 'open');
        };
    })
;

