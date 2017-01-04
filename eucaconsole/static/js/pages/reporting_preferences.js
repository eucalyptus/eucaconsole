angular.module('ReportingPage')
.controller('PreferencesController', ['$scope', '$routeParams', 'BucketService', 'eucaHandleError', 'ModalService', 'ReportingService',
function ($scope, $routeParams, BucketService, eucaHandleError, ModalService, ReportingService) {
    var vm = this;
    vm.defaultPolicy = '{ \n\
    "Version": "", \n\
    "Statement": [{ \n\
        "Effect": "Allow", \n\
        "Action": "s3:PutObject", \n\
        "Resource": "arn:aws:s3:::<bucket_name>/*", \n\
        "Principal": { \n\
            "AWS": "blah" \n\
        } \n\
    ] \n\
}';
    vm.values = {
        reportsEnabled: false,
        bucketName: '',
        bucketPolicy: vm.defaultPolicy,
        tagKeys: []
    }
    vm.buckets = [];
    vm.bucketPolicy = '';
    vm.tagKeyChoices = [];

    ReportingService.getReportingPrefs().then(
        function success(result) {
            var prefs = result.results;
            vm.values.reportsEnabled = prefs.enabled;
            vm.values.bucketName = prefs.bucketName;
            vm.values.tagKeys = prefs.activeTags;
            vm.tagKeyChoices = prefs.inactiveTags.concat(prefs.activeTags);
        },
        function error(errData) {
            eucaHandleError(errData.data.message, errData.status);
        });

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

    vm.saveChanges = function($event) {
        vm.savingChanges = true;
        ReportingService.setReportingPrefs(vm.values.reportsEnabled, vm.values.bucketName, vm.values.tagKeys, $('#csrf_token').val()).then(
            function success(result) {
                vm.savingChanges = false;
            },
            function error(errData) {
                vm.savingChanges = false;
                eucaHandleError(errData.data.message, errData.status);
            });
    };

    vm.showCreateBucket = function() {
        ModalService.openModal('createBucketDialog');
    };

    vm.showBucketPolicy = function() {
        vm.bucketPolicy = vm.values.bucketPolicy;
        ModalService.openModal('bucketPolicyDialog');
    };

    vm.saveBuckePolicy = function($event) {
        vm.values.bucketPolicy = vm.bucketPolicy;
        ModalService.closeModal('bucketPolicyDialog');
    };

    $scope.$watch('preferences.values.bucketName', function(newVal, oldVal) {
        if (newVal === oldVal) return;
        if (vm.buckets.indexOf(newVal) > -1) return;
        vm.buckets.push(newVal);
    });

    $scope.$on('$destroy', function () {
        ModalService.unregisterModals('createBucketDialog');
    });
}]);
