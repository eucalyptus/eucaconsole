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
        $scope.progress = 0;
        $scope.total = 0;
        $scope.chunkSize = 10;  // set this based on how many keys we want to delete at once
        $scope.index = 0;
        $scope.items = null;
        $scope.initController = function (deleteKeysUrl) {
            $scope.deleteKeysUrl = deleteKeysUrl;
        };
        $scope.revealModal = function (action, bucket) {
            var modal = $('#' + action + '-bucket-modal');
            $scope.bucketName = bucket['name'];
            modal.foundation('reveal', 'open');
        };
        $scope.deleteAll = function () {
            $scope.deletingAll = true;
            $scope.total = $scope.items.length;
            $scope.index = 0;
            $scope.deleteChunk();
        };
        $scope.deleteChunk = function () {
            var start = $scope.index * $scope.chunkSize;
            var end = start + $scope.chunkSize;
            if (end > $scope.total) {
                end = $scope.total;
            }
            var chunk = $scope.items.slice(start, end);
            var names = [];
            for (var j=0; j < chunk.length; j++) {
                names.push(chunk[j].name);
            }
            console.log("chunk : "+names.join(','));
            var data = "csrf_token="+$('#csrf_token').val()+"&keys="+names.join(',');
            $http({method:'POST', url:$scope.deleteKeysUrl, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                if (oData.errors !== undefined) {
                    console.log('error deleting some keys '+oData.errors);
                }
                var chunks = $scope.total / $scope.chunkSize;
                if ($scope.index >= chunks) {
                    Notify.success(oData.message);
                }
                else {
                    $scope.index += 1;
                    $scope.deleteChunk();
                }
              }).
              error(function (oData, status) {
                console.log("some kind of error");
              });
        };
        $scope.$on('itemsLoaded', function($event, items) {
            $scope.items = items;
            $scope.total = items.length;
        });
    })
;

