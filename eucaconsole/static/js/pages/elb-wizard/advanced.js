angular.module('ELBWizard')
.controller('AdvancedController', ['$scope', '$routeParams', 'ELBWizardService', 'ELBService', 'BucketService', 'eucaHandleError', 'ModalService',
function ($scope, $routeParams, ELBWizardService, ELBService, BucketService, eucaHandleError, ModalService) {
    var vm = this;
    vm.values = ELBWizardService.values;
    vm.buckets = [];
    vm.createELB = function($event) {
        $event.preventDefault();
        ELBService.createELB($('#csrf_token').val(), this.values).then(
            function success() {
                console.log('created ELB!');
            },
            function failure() {
                console.log('did not ELB!');
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
}])
.directive('loggingConfirmDialog', function() {
    return {
        restrict: 'A',
        require: ['^modal', 'loggingConfirmDialog'],
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

