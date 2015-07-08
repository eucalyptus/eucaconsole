/**
 * @fileOverview Create Bucket JS
 * @requires AngularJS and jQuery
 *
 */
angular.module('CreateBucketDialog', [])
    .controller('CreateBucketDialogCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketDialog = $('#create-bucket-modal');
        $scope.createBucketForm = $('#create-bucket-form');
        $scope.bucketName = '';
        $scope.existingBucketConflict = false;
        $scope.isCreatingBucket = false;
        $scope.handleCreateBucket = function (postUrl, $event) {
            $event.preventDefault();
            var formData = $($event.target).serialize();
            $scope.createBucketForm.trigger('validate');
            if ($scope.createBucketForm.find('[data-invalid]').length) {
                return false;
            }
            $scope.isCreatingBucket = true;
            $http({
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                method: 'POST',
                url: postUrl,
                data: formData
            }).success(function (oData) {
                // TODO: Add new bucket to choices and set it as selected
                $scope.isCreatingBucket = false;
                $scope.bucketDialog.foundation('reveal', 'close');
            }).error(function (oData) {
                if (oData.message) {
                    Notify.failure(oData.message);
                    $scope.isCreatingBucket = false;
                }
            });
        };
    })
;
