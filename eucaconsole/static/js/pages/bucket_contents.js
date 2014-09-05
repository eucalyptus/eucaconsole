/**
 * @fileOverview Bucket detail (contents) page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('BucketContentsPage', ['LandingPage'])
    .controller('BucketContentsCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketName = '';
        $scope.prefix = '';
        $scope.deletingAll = false;
        $scope.progress = 0;
        $scope.total = 0;
        $scope.chunkSize = 10;  // set this based on how many keys we want to delete at once
        $scope.index = 0;
        $scope.items = null;
        $scope.initController = function (deleteKeysUrl, getKeysUrl, prefix) {
            $scope.deleteKeysUrl = deleteKeysUrl;
            $scope.getKeysUrl = getKeysUrl;
            $scope.prefix = prefix;
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
            var data = "csrf_token="+$('#csrf_token').val()+"&keys="+names.join(',');
            $http({method:'POST', url:$scope.deleteKeysUrl, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                console.log(oData);
              }).
              error(function (oData, status) {
                console.log("some kind of error");
              });
        };
        $scope.deleteChunk = function () {
            var start = 0;
            var end = start + $scope.chunkSize;
            if (end > $scope.total) {
                end = $scope.total;
            }
            var chunk = $scope.items.slice(start, end);
            var names = [];
            for (var j=0; j < chunk.length; j++) {
                if ($scope.prefix.length > 0) {
                    names.push($scope.prefix+'/'+chunk[j].name);
                }
                else {
                    names.push(chunk[j].name);
                }
            }
            console.log("chunk : "+names.join(','));
            var data = "csrf_token="+$('#csrf_token').val()+"&keys="+names.join(',');
            $http({method:'POST', url:$scope.deleteKeysUrl, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                if (oData.errors !== undefined) {
                    console.log('error deleting some keys '+oData.errors);
                }
                $scope.progress = $scope.progress + $scope.chunkSize;
                if ($scope.progress > $scope.total) {
                    $scope.progress = $scope.total;
                }
                for (var i=0; i<$scope.chunkSize; i++) { // remove deleted items from table
                    $scope.items.shift();
                }
                if ($scope.deletingAll == true) {
                    var chunks = $scope.total / $scope.chunkSize;
                    $scope.index = $scope.index + 1;
                    if ($scope.index >= chunks) {
                        Notify.success(oData.message);
                        $('#delete-all-modal').foundation('reveal', 'close');
                    }
                    else {
                        $scope.deleteChunk();
                    }
                }
              }).
              error(function (oData, status) {
                console.log("some kind of error");
              });
        };
        $scope.cancelDeleting = function () {
            $scope.deletingAll = false;
            $('#delete-all-modal').foundation('reveal', 'close');
            $scope.$broadcast('refresh');
        };
        $scope.$on('itemsLoaded', function($event, items) {
            $scope.items = items;
            $scope.total = items.length;
        });
    })
;

