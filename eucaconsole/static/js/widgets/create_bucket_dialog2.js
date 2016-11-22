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
        controller: ['$scope', '$http', 'eucaHandleError', 'ModalService', function ($scope, $http, eucaHandleError, ModalService) {
            var vm = this;
            $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
            vm.existingBucketConflict = false;
            vm.isCreatingBucket = false;
            vm.bucketName = '';
            vm.handleCreateBucket = function ($event) {
                $event.preventDefault();
                if ($scope.createBucketForm.$invalid) {
                    return false;
                }
                var formData = {
                    'csrf_token': $('#csrf_token').val(),
                    'bucket_name': vm.bucketName
                };
                vm.isCreatingBucket = true;
                $http({
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    method: 'POST',
                    url: '/buckets/create_xhr',
                    data: $.param(formData)
                }).success(function (oData) {
                    $scope.bucketName = vm.bucketName;
                    vm.isCreatingBucket = false;
                    ModalService.closeModal('createBucketDialog');
                }).error(function (oData) {
                    eucaHandleError(oData);
                    vm.isCreatingBucket = false;
                });
            };
        }],
        controllerAs: 'createBucket'
    };
});
