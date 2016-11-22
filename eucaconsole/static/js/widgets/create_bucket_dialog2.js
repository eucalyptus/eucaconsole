/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Create Bucket JS
 * @requires AngularJS and jQuery
 *
 */
angular.module('CreateBucketModule', ['ModalModule', 'EucaConsoleUtils'])
.directive('createBucketDialog', function() {
    return {
        restrict: 'A',
        require: ['^modal', 'createBucketDialog', 'bucketName'],
        scope: {
            bucketName: '='
        },
        templateUrl: '/_template/dialogs/create_bucket_dialog2',
        controller: ['$scope', '$http', 'eucaHandleError', function ($scope, $http, eucaHandleError) {
            var vm = this;
            $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
            vm.existingBucketConflict = false;
            vm.isCreatingBucket = false;
            vm.handleCreateBucket = function ($event) {
                $event.preventDefault();
                if ($scope.create-bucket-form.$invalid) {
                    return false;
                }
                var formData = {
                    'csrf_token': $('#csrf_token').val(),
                    'bucket_name': $scope.bucketName
                };
                vm.isCreatingBucket = true;
                $http({
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    method: 'POST',
                    url: '/buckets/create_xhr',
                    data: $.param(formData)
                }).success(function (oData) {
                    vm.isCreatingBucket = false;
                    //$scope.bucketDialog.foundation('reveal', 'close');
                }).error(function (oData) {
                    eucaHandleError(oData);
                    vm.isCreatingBucket = false;
                });
            };
        }],
        controllerAs: createBucket
    };
});
