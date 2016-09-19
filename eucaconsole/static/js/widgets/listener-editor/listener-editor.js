angular.module('ELBListenerEditorModule', [])
.directive('listenerEditor', function () {
    return {
        restrict: 'E',
        scope: {
            listeners: '=ngModel'
        },
        templateUrl: '/_template/elbs/listener-editor/listener-editor',
        controller: ['$scope', function ($scope) {
            var vm = this;
            vm.from = {};
            vm.to = {};

            this.clientSideValid = function () {
                return !!(vm.from.port && vm.from.protocol);
            };

            this.portsValid = function () {
                var fromValid = !!(vm.from.port && vm.from.protocol);
                var toValid = !!(vm.to.port && vm.to.protocol);

                return fromValid && toValid;
            };

            this.removeListener = function (index) {
                $scope.listeners.splice(index, 1);
            };

            this.addListener = function () {
                if(!vm.portsValid()) {
                    return;
                }

                var listener = {
                    fromPort: vm.from.port,
                    fromProtocol: vm.from.protocol,
                    toPort: vm.to.port,
                    toProtocol: vm.to.protocol
                };
                $scope.listeners.push(listener);

                vm.from = {};
                vm.to = {};
            };
        }],
        controllerAs: 'ctrl'
    };
})
.directive('protocolPort', function () {
    var protocols = [
        {'name': 'HTTP', 'value': 'HTTP', 'port': 80},
        {'name': 'HTTPS', 'value': 'HTTPS', 'port': 443},
        {'name': 'TCP', 'value': 'TCP', 'port': 80},
        {'name': 'SSL', 'value': 'SSL', 'port': 443}
    ];

    return {
        restrict: 'E',
        require: 'ngModel',
        scope: {
            target: '=ngModel',
            label: '@'
        },
        templateUrl: '/_template/elbs/listener-editor/protocol-port',
        link: function (scope, element, attrs, ctrl) {
            var protocolField = element.find('select'),
                portField = element.find('input');

            protocolField.on('change blur', updateViewValue);
            portField.on('change blur', updateViewValue);

            function updateViewValue () {
                var protocol = protocolField.val(),
                    port = portField.val();

                ctrl.$setViewValue({
                    protocol: protocol,
                    port: port
                });
            }

            ctrl.$render = function () {
                protocolField.val(scope.target.protocol);
                portField.val(scope.target.port);
            };
        },
        controller: ['$scope', function ($scope) {
            this.protocols = protocols;

            this.onUpdate = function (protocol) {
                $scope.port = protocol.port;
            };
        }],
        controllerAs: 'ctrl'
    };
})
.directive('validListener', function () {
    return {
        require: 'ngModel',
        link: function (scope, element, attrs, ctrl) {
            ctrl.$validators.validListener = function (modelValue, viewValue) {
                if(modelValue.protocol === undefined) {
                    return false;
                }
                return true;
            };
        }
    };
});
