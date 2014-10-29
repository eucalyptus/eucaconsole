/**
 * @fileOverview Bucket detail (contents) page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('BucketContentsPage', ['LandingPage', 'EucaConsoleUtils'])
    .controller('BucketContentsCtrl', function ($scope, $http, eucaUnescapeJson, eucaHandleErrorS3) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketName = '';
        $scope.prefix = '';
        $scope.folder = '';  // gets set if we are deleting/copying a folder specifically
        $scope.obj_key = '';  // gets set if we are deleting an object specifically
        $scope.deletingAll = false;
        $scope.copyingAll = false;
        $scope.progress = 0;
        $scope.total = 0;
        $scope.chunkSize = 10;  // set this based on how many keys we want to delete at once
        $scope.index = 0;
        $scope.items = null;
        $scope.op_prefix = '';
        $scope.hasCopyItem = false;
        $scope.hasCopyFolder = false;
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.bucketName = options['bucket_name'];
            $scope.deleteKeysUrl = options['delete_keys_url'];
            $scope.getKeysUrl = options['get_keys_url'];
            $scope.prefix = options['key_prefix'];
            $scope.copyObjUrl = options['copy_object_url'];
            $scope.getKeysGenericUrl = options['get_keys_generic_url'];
            $scope.putKeysUrl = options['put_keys_url'];
            // set upload button target based on media query
            if (window.matchMedia(Foundation.media_queries['small']).matches === false) {
                $('#upload-file-btn').attr('target', '_blank');
            }
            $scope.updatePasteValues();
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
                    eucaHandleErrorS3(oData, status);
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
                    eucaHandleErrorS3(oData, status);
                });
        };
        $scope.updatePasteValues = function() {
            $scope.pasteBuffer = Modernizr.sessionstorage && sessionStorage.getItem('copy-object-buffer');
            $scope.hasCopyItem = false;
            $scope.hasCopyFolder = false;
            if ($scope.pasteBuffer !== null) {
                $scope.pasteBucket = $scope.pasteBuffer.slice(0, $scope.pasteBuffer.indexOf('/'));
                $scope.pasteKey = $scope.pasteBuffer.slice($scope.pasteBuffer.indexOf('/')+1);
                $scope.pastePath = $scope.pasteKey.slice(0, $scope.pasteKey.slice(0, $scope.pasteKey.length-1).lastIndexOf('/')+1);
                var prefix = $scope.prefix;
                if (prefix.length > 0) {
                    prefix = prefix + '/';
                }
                // initially, set based on key ending
                if ($scope.pasteBuffer.indexOf('/', $scope.pasteBuffer.length - 1) !== -1) {
                    $scope.hasCopyFolder = true;
                    // detect copy on self
                    if ($scope.pasteBucket == $scope.bucketName && $scope.pastePath == prefix) {
                        $scope.hasCopyFolder = false;
                    }
                }
                else {
                    $scope.hasCopyItem = true;
                    // detect copy on self
                    if ($scope.pasteBucket == $scope.bucketName && $scope.pastePath == prefix) {
                        $scope.hasCopyItem = false;
                    }
                }
            }
        };
        $scope.folderCanCopyFolder = function (item) {
            if (item && $scope.pasteBucket == $scope.bucketName && $scope.pastePath == item.full_key_name) {
                return false;
            }
            return $scope.hasCopyFolder;
        };
        $scope.saveKey = function (bucket_name, key) {
            var id = $('.open').attr('id');  // hack to close action menu
            $('#table-'+id).trigger('click');
            Modernizr.sessionstorage && sessionStorage.setItem('copy-object-buffer', bucket_name + '/' + key);
            $scope.updatePasteValues();
        };
        $scope.$on('itemsLoaded', function($event, items) {
            $scope.items = items;
        });
        $scope.doPaste = function (bucketName, item, subpath) {
            var id = $('.open').attr('id');  // hack to close action menu
            $('#table-'+id).trigger('click');
            var path = Modernizr.sessionstorage && sessionStorage.getItem('copy-object-buffer');
            if (path.indexOf('/', path.length - 1) !== -1) {
                // this is a folder, so send it off to the folder handling code
                if (item === null) {
                    $scope.op_prefix = $scope.prefix;
                }
                else {
                    $scope.op_prefix = item.full_key_name;
                }
                $scope.startFolderCopy(path);
                return;
            }
            var bucket = path.slice(0, path.indexOf('/'));
            var key = path.slice(path.indexOf('/')+1);
            if (subpath === undefined) {
                subpath = item.details_url.slice(item.details_url.indexOf('itemdetails')+12);
            }
            for (var i=0; i<$scope.items.length; i++) {
                this_key = $scope.items[i].name;
                if (subpath.length > 0) {
                    this_key = subpath + '/' + this_key;
                }
                if (key == this_key) {
                    $('#copy-on-self-warn-modal').foundation('reveal', 'open');
                    return;
                }
            }
            var url = $scope.copyObjUrl.replace('_name_', bucketName).replace('_subpath_', subpath);
            var data = "csrf_token="+$('#csrf_token').val()+'&src_bucket='+bucket+'&src_key='+key;
            $http({method:'POST', url:url, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                if (oData.error == undefined) {
                    if (!item) {  // in case where we're pasting in current context,
                        $scope.$broadcast('refresh');
                    }
                } else {
                    Notify.failure(oData.message);
                }
              }).
              error(function (oData, status) {
                eucaHandleErrorS3(oData, status);
              });
        };
        $scope.startFolderCopy = function (path) {
            $scope.src_bucket = path.slice(0, path.indexOf('/'));
            $scope.src_path = path.slice(path.indexOf('/')+1);
            var url = $scope.getKeysGenericUrl;
            url = url.replace('_name_', $scope.src_bucket);
            url = url.replace('_subpath_', $scope.src_path);
            // slice and dice to get portion of path to be excluded in new location
            $scope.folder = $scope.src_path.slice(0, $scope.src_path.slice(0, $scope.src_path.length-1).lastIndexOf('/')+1);
            var data = "csrf_token="+$('#csrf_token').val();
            $http({method: 'POST', url: url, data: data,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                success(function (oData) {
                    $scope.total = oData.results.length;
                    $scope.all_items = oData.results;
                    $scope.index = 0;
                    $('#copy-folder-modal').foundation('reveal', 'open');
                    $scope.copyFolder();
                }).
                error(function (oData, status) {
                    Notify.failure(oData.message);
                });
        };
        $scope.copyFolder = function () {
            $scope.copyingAll = true;
            $scope.copyChunk();
        };
        $scope.copyChunk = function () {
            var start = $scope.index * $scope.chunkSize;
            var end = start + $scope.chunkSize;
            if (end > $scope.total) {
                end = $scope.total;
            }
            var chunk = $scope.all_items.slice(start, end);
            var escapedChunk = chunk.map(function (key_name) {
                return encodeURIComponent(key_name);
            });
            var url = $scope.putKeysUrl.replace('_subpath_', $scope.op_prefix);
            var data = "csrf_token=" + $('#csrf_token').val() +
                       "&src_bucket=" + $scope.src_bucket +
                       "&folder_loc=" + $scope.folder +
                       "&keys=" + escapedChunk.join(',');
            $http({method: 'POST', url: url, data: data,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                success(function (oData) {
                    if (oData.errors !== undefined) {
                        console.log('error copying some keys ' + oData.errors);
                    }
                    $scope.progress = $scope.progress + $scope.chunkSize;
                    if ($scope.progress > $scope.total) {
                        $scope.progress = $scope.total;
                    }
                    if ($scope.copyingAll == true) {
                        var chunks = $scope.total / $scope.chunkSize;
                        $scope.index = $scope.index + 1;
                        if ($scope.index >= chunks) {
                            $('#copy-folder-modal').foundation('reveal', 'close');
                            $scope.copyingAll = false;
                            $scope.folder = '';
                            $scope.$broadcast('refresh');
                        }
                        else {
                            $scope.copyChunk();
                        }
                    }
                }).
                error(function (oData, status) {
                    $('#copy-folder-modal').foundation('reveal', 'close');
                    $scope.copyingAll = false;
                    Notify.failure("some kind of error");
                });
        };
        $scope.cancelCopying = function () {
            $('#copy-folder-modal').foundation('reveal', 'close');
            $scope.copyingAll = false;
            $scope.$broadcast('refresh');
        };
    })
;

