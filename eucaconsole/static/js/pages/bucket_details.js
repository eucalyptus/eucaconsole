/**
 * @fileOverview Bucket detail page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('BucketDetailsPage', [])
    .controller('BucketDetailsPageCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.initController = function () {

        };
    })
;

