/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Create Bucket JS
 * @requires AngularJS and jQuery
 *
 */
angular.module('CreateBucketModule', ['ModalModule', 'EucaConsoleUtils', 'BucketServiceModule'])
.directive('createBucketDialog', function() {
    return {
        restrict: 'A',
        scope: {
            bucketName: '='
        },
        templateUrl: '/_template/dialogs/create_bucket_dialog2',
        controller: ['$scope', '$http', 'eucaHandleError', 'ModalService', 'BucketService', 
        function ($scope, $http, eucaHandleError, ModalService, BucketService) {
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
                vm.isCreatingBucket = true;
                BucketService.createBucket(vm.bucketName, $('#csrf_token').val()).then(
                    function success(oData) {
                        $scope.bucketName = vm.bucketName;
                        vm.isCreatingBucket = false;
                        ModalService.closeModal('createBucketDialog');
                    },
                    function error(oData) {
                        eucaHandleError(oData);
                        vm.isCreatingBucket = false;
                    }
                );
            };
        }],
        controllerAs: 'createBucket'
    };
});
