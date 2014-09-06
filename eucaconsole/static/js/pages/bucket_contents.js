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
        $scope.revealModal = function (action) {
            var modal = $('#' + action + '-modal');
            if (action == 'delete-all') {
                var data = "csrf_token="+$('#csrf_token').val();
                $http({method:'POST', url:$scope.getKeysUrl, data:data,
                       headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                  success(function(oData) {
                    $scope.total = oData.results.length;
                    $scope.all_items = oData.results;
                    $scope.index = 0;
                    modal.foundation('reveal', 'open');
                  }).
                  error(function (oData, status) {
                    Notify.failure(oData.message);
                  });
            }
            else {
                modal.foundation('reveal', 'open');
            }
        };
        $scope.deleteAll = function () {
            $scope.deletingAll = true;
            $scope.deleteChunk();
        };
        $scope.deleteChunk = function () {
            var start = $scope.index * $scope.chunkSize;
            var end = start + $scope.chunkSize;
            if (end > $scope.total) {
                end = $scope.total;
            }
            var chunk = $scope.all_items.slice(start, end);
            var data = "csrf_token="+$('#csrf_token').val()+"&keys="+chunk.join(',');
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
                for (var i=0; i<chunk.length; i++) { // remove deleted items from table
                    for (var j=0; j<$scope.items.length; j++) {
                        var name = chunk[i].split('/').pop();
                        if (name.indexOf('_$folder$') > -1) {
                            name = name.slice(0, name.length - 9);
                        }
                        if (name == $scope.items[j].name) {
                            $scope.items.splice(j, 1);
                        }
                    }
                }
                if ($scope.deletingAll == true) {
                    var chunks = $scope.total / $scope.chunkSize;
                    $scope.index = $scope.index + 1;
                    if ($scope.index >= chunks) {
                        $scope.deletingAll = false;
                        Notify.success(oData.message);
                        $('#delete-all-modal').foundation('reveal', 'close');
                    }
                    else {
                        $scope.deleteChunk();
                    }
                }
              }).
              error(function (oData, status) {
                Notify.failure("some kind of error");
              });
        };
        $scope.cancelDeleting = function () {
            $scope.deletingAll = false;
            $('#delete-all-modal').foundation('reveal', 'close');
            $scope.$broadcast('refresh');
        };
        $scope.$on('itemsLoaded', function($event, items) {
            $scope.items = items;
        });
    })
;

