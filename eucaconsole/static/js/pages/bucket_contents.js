/**
 * @fileOverview Bucket detail (contents) page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('BucketContentsPage', ['LandingPage', 'EucaConsoleUtils'])
    .controller('BucketContentsCtrl', function ($scope, $http, eucaUnescapeJson) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketName = '';
        $scope.prefix = '';
        $scope.folder = '';  // gets set if we are deleting a folder specifically
        $scope.obj_key = '';  // gets set if we are deleting an object specifically
        $scope.deletingAll = false;
        $scope.progress = 0;
        $scope.total = 0;
        $scope.chunkSize = 10;  // set this based on how many keys we want to delete at once
        $scope.index = 0;
        $scope.items = null;
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.deleteKeysUrl = options['delete_keys_url'];
            $scope.getKeysUrl = options['get_keys_url'];
            $scope.prefix = options['key_prefix'];
            $scope.copyObjUrl = options['copy_object_url'];
            // set upload button target based on media query
            if (window.matchMedia(Foundation.media_queries['small']).matches === false) {
                $('#upload-file-btn').attr('target', '_blank');
            }
        };
        $scope.revealModal = function (action, item) {
            var modal = $('#' + action + '-modal');
            if (action == 'delete-all' || action == 'delete-folder') {
                var url = $scope.getKeysUrl;
                $scope.folder = '';
                if (action == 'delete-folder') {
                    url = url + '/' + encodeURIComponent(item.name);
                    $scope.folder = item.name;
                }
                var data = "csrf_token="+$('#csrf_token').val();
                $http({method: 'POST', url: url, data: data,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                    success(function (oData) {
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
                $scope.obj_key = item.name;
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
            var escapedChunk = chunk.map(function (key_name) {
                return encodeURIComponent(key_name);
            });
            var data = "csrf_token=" + $('#csrf_token').val() + "&keys=" + escapedChunk.join(',');
            $http({method: 'POST', url: $scope.deleteKeysUrl, data: data,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                success(function (oData) {
                    if (oData.errors !== undefined) {
                        console.log('error deleting some keys ' + oData.errors);
                    }
                    $scope.progress = $scope.progress + $scope.chunkSize;
                    if ($scope.progress > $scope.total) {
                        $scope.progress = $scope.total;
                    }
                    if ($scope.folder == '') {
                        for (var i = 0; i < chunk.length; i++) { // remove deleted items from table
                            for (var j = 0; j < $scope.items.length; j++) {
                                var name = chunk[i].split('/').pop();
                                if (name.indexOf('_$folder$') > -1) {
                                    name = name.slice(0, name.length - 9);
                                }
                                if (name == $scope.items[j].name) {
                                    $scope.items.splice(j, 1);
                                }
                            }
                        }
                    }
                    if ($scope.deletingAll == true) {
                        var chunks = $scope.total / $scope.chunkSize;
                        $scope.index = $scope.index + 1;
                        if ($scope.index >= chunks) {
                            $scope.deletingAll = false;
                            Notify.success(oData.message);
                            if ($scope.folder != '') {
                                $('#delete-folder-modal').foundation('reveal', 'close');
                                for (var j = 0; j < $scope.items.length; j++) {
                                    var name = $scope.folder;
                                    if (name.indexOf('_$folder$') > -1) {
                                        name = name.slice(0, name.length - 9);
                                    }
                                    if (name == $scope.items[j].name) {
                                        $scope.items.splice(j, 1);
                                    }
                                }
                                $scope.folder = '';
                            }
                            else {
                                $('#delete-all-modal').foundation('reveal', 'close');
                            }
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
        $scope.deleteObject = function () {
            var data = "csrf_token=" + $('#csrf_token').val() + "&keys=" + $scope.prefix + '/' + $scope.obj_key;
            $http({method: 'POST', url: $scope.deleteKeysUrl, data: data,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                success(function (oData) {
                    if (oData.errors !== undefined) {
                        console.log('error deleting some keys ' + oData.errors);
                    }
                    for (var j = 0; j < $scope.items.length; j++) {
                        var name = $scope.obj_key;
                        if (name == $scope.items[j].name) {
                            $scope.items.splice(j, 1);
                        }
                    }
                    $('#delete-object-modal').foundation('reveal', 'close');
                    Notify.success(oData.message);
                    $scope.obj_key = '';
                }).
                error(function (oData, status) {
                    Notify.failure("some kind of error");
                });
        };
        $scope.saveKey = function (path, key) {
            var id = $('.open').attr('id');  // hack to close action menu
            $('#table-'+id).trigger('click');
            Modernizr.localstorage && localStorage.setItem('copy-object-buffer', path+'/'+key);
        };
        $scope.$on('itemsLoaded', function($event, items) {
            $scope.items = items;
        });
        $scope.hasCopyItem = function () {
            return Modernizr.localstorage && localStorage.getItem('copy-object-buffer');
        };
        $scope.doPaste = function (bucketName, item, subpath) {
            var id = $('.open').attr('id');  // hack to close action menu
            $('#table-'+id).trigger('click');
            var path = Modernizr.localstorage && localStorage.getItem('copy-object-buffer');
            var bucket = path.slice(0, path.indexOf('/'));
            var key = path.slice(path.indexOf('/')+1);
            if (subpath === undefined) {
                subpath = item.details_url.slice(item.details_url.indexOf('itemdetails')+12);
            }
            var url = $scope.copyObjUrl.replace('_name_', bucketName).replace('_subpath_', subpath);
            var data = "csrf_token="+$('#csrf_token').val()+'&src_bucket='+bucket+'&src_key='+key;
            $http({method:'POST', url:url, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                if (oData.error == undefined) {
                    Modernizr.localstorage && localStorage.removeItem('copy-object-buffer');
                    if (!item) {  // in case where we're pasting in current context,
                        $scope.$broadcast('refresh');
                    }
                } else {
                    Notify.failure(oData.message);
                }
              }).
              error(function (oData, status) {
                var errorMsg = oData['message'] || '';
                Notify.failure(errorMsg);
              });
        };
    })
;

