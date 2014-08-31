/**
 * @fileOverview Bucket item (folder/object) detail page JS
 * @requires AngularJS, jQuery
 *
 */

/* Bucket item details page includes the S3 Sharing Panel */
angular.module('BucketItemDetailsPage', ['S3SharingPanel'])
    .controller('BucketItemDetailsPageCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.objectsCountLoading = true;
        $scope.initController = function () {
        };
    })
;

