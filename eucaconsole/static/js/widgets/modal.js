/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview directive and factory to manage modal dialogs
 * @requires AngularJS, jQuery
 *
 */
angular.module('ModalModule', [])
.directive('modal', ['ModalService', '$interpolate', function (ModalService, $interpolate) {
    var template = '<div class="modal-bg" ng-click="closeModal(\'{{modalName}}\')"></div><div class="modal-content">' +
        '<a ng-click="closeModal(\'{{modalName}}\')" class="close-modal">×</a><ng-transclude></ng-transclude></div>';
    return {
        restrict: 'A',
        transclude: true,
        compile: function (tElem, tAttrs) {
            var tmp = $interpolate(template)({modalName:tAttrs.modal});
            tElem.append(tmp);
            return function (scope, element, attrs) {
                ModalService.registerModal(attrs.modal, element);

                // Set the height of the containing div based upon the content
                // height of the modal content.
                var el = angular.element(element);
                var content = el.find('.modal-content');

                scope.$watch(function () {
                    return content.height();
                }, function (newVal, oldVal) {
                    if(newVal !== oldVal) {
                        element.height(newVal);
                    }
                });
            };
        },
        controller: ['$scope', function ($scope) {
            $scope.closeModal = function (name) {
                ModalService.closeModal(name);
            };
        }]
    };
}])
.factory('ModalService', ['$rootScope', function ($rootScope) {
    var _modals = {};

    function registerModal (name, element) {
        if(name in _modals) {
            throw new Error('Modal with name ' + name + ' already registered.');
        }
        _modals[name] = element;
    }

    function unregisterModals () {
        for(var i = 0; i < arguments.length; i++ ) {
            var name = arguments[i];
            delete _modals[name];
        }
    }

    function openModal (name) {
        var modal = _modals[name];
        if(!modal) {
            return;
        }
        modal.addClass('open');
        $rootScope.$broadcast('modal:open', name);
    }

    function closeModal (name) {
        var modal = _modals[name];
        if(!modal) {
            return;
        }

        modal.removeClass('open');
        $rootScope.$broadcast('modal:close', name);
    }

    function _getModals () {
        return _modals;
    }

    function _clearModals () {
        _modals = {};
    }

    return {
        openModal: openModal,
        closeModal: closeModal,
        registerModal: registerModal,
        unregisterModals: unregisterModals,
        _getModals: _getModals,
        _clearModals: _clearModals
    };
}]);
