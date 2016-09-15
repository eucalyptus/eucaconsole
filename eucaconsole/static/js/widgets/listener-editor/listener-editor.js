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
            vm.clientSide = {};
            vm.serverSide = {};

            this.removeListener = function (index) {
                $scope.listeners.splice(index, 1);
            };

            this.addListener = function () {
                var listener = {
                    fromPort: vm.clientSide.port,
                    fromProtocol: vm.clientSide.protocol,
                    toPort: vm.clientSide.port,
                    toProtocol: vm.clientSide.protocol
                };
                $scope.listeners.push(listener);
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
        require: '^listenerEditor',
        scope: {
            target: '=ngModel',
            label: '@'
        },
        templateUrl: '/_template/elbs/listener-editor/protocol-port',
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
            var protocolField = element.find('select'),
                portField = element.find('input');

            ctrl.$validators.validListener = function (modelValue, viewValue) {
                if(modelValue.protocol === undefined) {
                    return false;
                }
                return true;
            };

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
        }
    };
});
