angular.module('ELBWizard')
.controller('AdvancedController', ['$scope', '$routeParams', '$window', 'ELBWizardService', 'ELBService', 'BucketService', 'eucaHandleError', 'ModalService',
function ($scope, $routeParams, $window, ELBWizardService, ELBService, BucketService, eucaHandleError, ModalService) {
    var vm = this;
    vm.values = ELBWizardService.values;
    vm.buckets = [];
    vm.creatingELB = false;
    vm.createELB = function($event) {
        $event.preventDefault();
        if($scope.advancedForm.$invalid) {
            return;
        }
        vm.creatingELB = true;
        ELBService.createELB($('#csrf_token').val(), this.values).then(
            function success(result) {
                $window.location = '/elbs';
            },
            function failure(errData) {
                eucaHandleError(errData.data.message, errData.status);
                vm.creatingELB = false;
            }
        );
    };
    vm.accessLogConfirmationDialogKey = 'doNotShowAccessLogConfirmationAgain';
    vm.handleLoggingChange = function() {
        if (vm.values.loggingEnabled) {
            if (vm.buckets.length === 0) {
                BucketService.getBuckets($('#csrf_token').val()).then(
                    function success(result) {
                        result.forEach(function(val) {
                            vm.buckets.push(val.bucket_name); 
                        });
                    },
                    function error(errData) {
                        eucaHandleError(errData.data.message, errData.status);
                    });
            }
            if (Modernizr.localstorage && !localStorage.getItem(vm.accessLogConfirmationDialogKey)) {
                ModalService.openModal('loggingConfirmDialog');
            }
        }
    };
    vm.showCreateBucket = function() {
        ModalService.openModal('createBucketDialog');
    };
    $scope.$watch('advanced.values.bucketName', function(newVal, oldVal) {
        if (newVal === oldVal) return;
        vm.buckets.push(newVal);
    });
}])
.directive('loggingConfirmDialog', function() {
    return {
        restrict: 'A',
        templateUrl: '/_template/elbs/wizard/logging-confirm-dialog',
        controller: ['ModalService', function(ModalService) {
            var vm = this;
            vm.accessLogConfirmationDialogKey = 'doNotShowAccessLogConfirmationAgain';
            vm.confirmEnableAccessLogs = function() {
                if (vm.dontShowBucketWarnAgain && Modernizr.localstorage) {
                    localStorage.setItem(vm.accessLogConfirmationDialogKey, true);
                }
                ModalService.closeModal('loggingConfirmDialog');
            };
        }],
        controllerAs: 'loggingConfirm'
    };
});

