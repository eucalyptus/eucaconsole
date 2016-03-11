angular.module('CreateAlarmModal', [])
.directive('modal', ['ModalService', '$document', function (ModalService, $document) {
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
.directive('createAlarm', ['MetricService', function (MetricService) {
    return {
        restrict: 'A',
        require: 'modal',
        link: function (scope, element, attrs) {
            scope.resourceType = attrs.resourceType;
            scope.resourceId = attrs.resourceId;
            scope.defaultMetric = attrs.defaultMetric;

            MetricService.getMetrics(scope.resourceType, scope.resourceId)
                .then(function (result) {
                    scope.metrics = result.data.metrics || [];
                });
        },
        controller: ['$scope', function ($scope) {
            console.log($scope);
            $scope.alarm = {};

            $scope.$watchCollection('alarm', function () {
                console.log($scope.alarm);
            });

            $scope.alarmName = function () {
                // Name field updates when metric selection changes,
                // unless the user has changed the value themselves.
            };
        }]
    };
}])
.factory('MetricService', ['$http', '$interpolate', function ($http, $interpolate) {
    var metricsUrl = $interpolate('/metrics/available/{{ resourceType }}/{{ resourceValue }}');

    return {
        getMetrics: function (resourceType, resourceValue) {
            return $http({
                method: 'GET',
                url: metricsUrl({
                    resourceType: resourceType,
                    resourceValue: resourceValue
                })
            });
        }
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
