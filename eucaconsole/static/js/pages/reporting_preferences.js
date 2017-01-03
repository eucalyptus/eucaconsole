angular.module('ReportingPage')
.controller('PreferencesController', ['$scope', '$routeParams', 'BucketService', 'eucaHandleError', 'ModalService',
function ($scope, $routeParams, BucketService, eucaHandleError, ModalService) {
    var vm = this;
    vm.bucketName = '';
    vm.tagKeys = [];
    vm.tagKeyChoices = ['one', 'two', 'three'];

    vm.showCreateBucket = function() {
        ModalService.openModal('createBucketDialog');
    };

    $scope.$on('$destroy', function () {
        ModalService.unregisterModals('createBucketDialog');
    });
}]);
