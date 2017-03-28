angular.module('ReportingPage')
.controller('PreferencesController', ['$scope', '$routeParams', 'BucketService', 'eucaHandleError', 'ModalService', 'ReportingService',
function ($scope, $routeParams, BucketService, eucaHandleError, ModalService, ReportingService) {
    var vm = this;
    vm.values = {
        reportsEnabled: false,
        bucketName: '',
        tagKeys: [],
        userReportsEnabled: false
    };
    vm.buckets = [];
    vm.tagKeyChoices = [];

    ReportingService.getReportingPrefs().then(
        function success(result) {
            var prefs = result.results;
            vm.values.reportsEnabled = prefs.enabled;
            vm.values.bucketName = prefs.bucketName;
            vm.values.tagKeys = prefs.activeTags;
            vm.tagKeyChoices = prefs.inactiveTags.concat(prefs.activeTags);
            vm.values.userReportsEnabled = prefs.userReportsEnabled;
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
        ReportingService.setReportingPrefs(vm.values.reportsEnabled, vm.values.bucketName,
                vm.values.tagKeys, vm.values.userReportsEnabled, $('#csrf_token').val()).then(
            function success(result) {
                Notify.success(result.message);
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

    $scope.$watch('preferences.values.bucketName', function(newVal, oldVal) {
        if (newVal === oldVal) return;
        if (vm.buckets.indexOf(newVal) > -1) return;
        vm.buckets.push(newVal);
    });

    $scope.$on('$destroy', function () {
        ModalService.unregisterModals('createBucketDialog');
    });
}]);
