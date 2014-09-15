/**
 * @fileOverview Buckets landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('BucketsPage', ['LandingPage'])
    .controller('BucketsCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketName = '';
        $scope.updateVersioningAction = '';
        $scope.bucketCounts = {};
        $scope.bucketVersioningStatus = {};
        $scope.bucketVersioningAction = {};
        $scope.countsLoading = {};
        $scope.versioningStatusLoading = {};
        $scope.initController = function (bucketObjectsCountUrl, updateVersioningFormUrl) {
            $scope.bucketObjectsCountUrl = bucketObjectsCountUrl;
            $scope.updateVersioningFormUrl = updateVersioningFormUrl;
        };
        $scope.revealModal = function (action, bucket) {
            var modal = $('#' + action + '-modal');
            $scope.bucketName = bucket['bucket_name'];
            $scope.bucketCount = $scope.bucketCounts[$scope.bucketName];
            $scope.updateVersioningAction = bucket['update_versioning_action'];
            // Set form action based on bucket choice
            var form_action = $('#' + action + '-form').attr('action');
            form_action = form_action.replace('_name_', $scope.bucketName);
            $('#' + action + '-form').attr('action', form_action);
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
    })
;

