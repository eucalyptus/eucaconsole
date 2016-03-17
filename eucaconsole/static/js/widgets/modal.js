angular.module('ModalModule', [])
.directive('modal', ['ModalService', function (ModalService) {
    return {
        restrict: 'A',
        template: '<div class="modal-bg"></div><div class="modal-content"><a ng-click="closeModal()" class="close-modal">×</a><ng-transclude></ng-transclude></div>',
        transclude: true,
        link: function (scope, element, attrs) {
            scope.modalName = attrs.modal;
            ModalService.registerModal(scope.modalName, element);
        },
        controller: ['$scope', function ($scope) {
            $scope.closeModal = function () {
                ModalService.closeModal($scope.modalName);
            };
        }]
    };
}])
.factory('ModalService', function () {
    var _modals = {};

    function registerModal (name, element) {
        if(name in _modals) {
            console.error('Modal with name ', name, ' already registered.');
            return;
        }
        _modals[name] = element;
    }

    function openModal (name) {
        var modal = _modals[name];
        if(!modal) {
            return;
        }

        modal.addClass('open');
    }

    function closeModal (name) {
        var modal = _modals[name];
        if(!modal) {
            return;
        }

        modal.removeClass('open');
    }

    return {
        openModal: openModal,
        closeModal: closeModal,
        registerModal: registerModal
    };
});
