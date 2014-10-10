/**
 * @fileOverview Buckets landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('BucketsPage', ['LandingPage', 'EucaConsoleUtils'])
    .controller('BucketsCtrl', function ($scope, $http, eucaUnescapeJson) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketName = '';
        $scope.updateVersioningAction = '';
        $scope.bucketCounts = {};
        $scope.versionCounts = {};
        $scope.bucketVersioningStatus = {};
        $scope.bucketVersioningAction = {};
        $scope.countsLoading = {};
        $scope.versioningStatusLoading = {};
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.bucketObjectsCountUrl = options['bucket_objects_count_url'];
            $scope.updateVersioningFormUrl = options['update_versioning_url'];
            $scope.copyObjUrl = options['copy_object_url'];
        };
        $scope.revealModal = function (action, bucket) {
            var modal = $('#' + action + '-modal');
            $scope.bucketName = bucket['bucket_name'];
            $scope.bucketCount = $scope.bucketCounts[$scope.bucketName];
            $scope.versionCount = $scope.versionCounts[$scope.bucketName];
            // Set form action based on bucket choice
            var form_action = $('#' + action + '-form').attr('action');
            form_action = form_action.replace('_name_', $scope.bucketName);
            $('#' + action + '-form').attr('action', form_action);
            modal.foundation('reveal', 'open');
        };
        $scope.revealVersioningModal = function (versioningAction, bucket) {
            // Need distinct handling of the versioning modal since bucket versioning info is lazy-loaded
            var modal = $('#update-versioning-modal');
            var versioningForm = $('#update-versioning-form');
            var form_action = versioningForm.attr('action');
            $scope.updateVersioningAction = versioningAction;
            $scope.bucketName = bucket['bucket_name'];
            $scope.bucketCount = $scope.bucketCounts[$scope.bucketName];
            // Set form action based on bucket choice
            form_action = form_action.replace('_name_', $scope.bucketName);
            versioningForm.attr('action', form_action);
            modal.foundation('reveal', 'open');
        };
        $scope.getVersioningActionFromStatus = function (versioningStatus) {
            if (versioningStatus == 'Disabled' || versioningStatus == 'Suspended') {
                return 'enable';
            }
            return 'disable';
        };
        $scope.$on('itemsLoaded', function($event, items) {
            angular.forEach(items, function(item, key) {
                var bucketName = item['bucket_name'];
                var objectsCountUrl = $scope.bucketObjectsCountUrl.replace('_name_', bucketName);
                $scope.countsLoading[bucketName] = true;
                $scope.versioningStatusLoading[bucketName] = true;
                $http.get(objectsCountUrl).success(function(oData) {
                    var results = oData ? oData.results : {},
                        versioningStatus = results['versioning_status'];
                    $scope.bucketCounts[bucketName] = results['object_count'];
                    $scope.versionCounts[bucketName] = results['version_count'];
                    $scope.bucketVersioningStatus[bucketName] = versioningStatus;
                    $scope.bucketVersioningAction[bucketName] = $scope.getVersioningActionFromStatus(versioningStatus);
                    $scope.countsLoading[bucketName] = false;
                    $scope.versioningStatusLoading[bucketName] = false;
                }).error(function (oData, status) {
                    var errorMsg = oData['message'] || null;
                    if (errorMsg) {
                        if (status === 403 || status === 400) {
                            $('#timed-out-modal').foundation('reveal', 'open');
                        } else {
                            Notify.failure(errorMsg);
                        }
                    }
                });
            });
        });
        $scope.hasCopyItem = function () {
            return Modernizr.sessionstorage && sessionStorage.getItem('copy-object-buffer');
        };
        $scope.doPaste = function (bucket) {
            var id = $('.open').attr('id');  // hack to close action menu
            $('#table-'+id).trigger('click');
            var bucketName = bucket['bucket_name'];
            var path = Modernizr.sessionstorage && sessionStorage.getItem('copy-object-buffer');
            var bucket = path.slice(0, path.indexOf('/'));
            var key = path.slice(path.indexOf('/') + 1);
            var url = $scope.copyObjUrl.replace('_name_', bucketName).replace('_subpath_', '');
            var data = "csrf_token=" + $('#csrf_token').val() + '&src_bucket=' + bucket + '&src_key=' + key;
            $http({method:'POST', url:url, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                if (oData.error == undefined) {
                    Modernizr.sessionstorage && sessionStorage.removeItem('copy-object-buffer');
                    $scope.$broadcast('refresh');
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

