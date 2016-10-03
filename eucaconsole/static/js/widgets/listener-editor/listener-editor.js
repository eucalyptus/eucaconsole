angular.module('ELBListenerEditorModule', ['ModalModule'])
.directive('listenerEditor', function () {
    return {
        restrict: 'E',
        scope: {
            listeners: '=ngModel'
        },
        templateUrl: '/_template/elbs/listener-editor/listener-editor',
        controller: ['$scope', 'ModalService', function ($scope, ModalService) {
            var vm = this;

            this.from = {};
            this.to = {};

            this.protocols = [
                {name: 'Select...', value: 'None', port: ''},
                {name: 'HTTP', value: 'HTTP', port: 80},
                {name: 'HTTPS', value: 'HTTPS', port: 443},
                {name: 'TCP', value: 'TCP', port: 80},
                {name: 'SSL', value: 'SSL', port: 443}
            ];

            this.targetValid = function (target) {
                return !!(target.port && target.protocol !== 'None');
            };

            this.portsValid = function () {
                var fromValid = this.targetValid(vm.from);
                var toValid = this.targetValid(vm.to);

                // Load balancer port must be either 25, 80, 443, 465, 587 or from 1024 to 65535
                // Selected port is already in use by another listener. Please select an unused port.

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

                vm.reset();
            };

            this.reset = function () {
                vm.from = vm.protocols[0];
                vm.to = vm.protocols[0];
            };
            this.cancel = this.reset;

            this.openPolicyModal = function () {
                ModalService.openModal('securityPolicyEditor');
            };

            this.openCertificateModal = function () {
                ModalService.openModal('certificateEditor');
            };
        }],
        controllerAs: 'ctrl'
    };
})
.directive('protocolPort', function () {

    var validPorts = [25, 80, 443, 465, 587],
        validPortMin = 1024,
        validPortMax = 65535;

    return {
        restrict: 'E',
        require: 'ngModel',
        scope: {
            target: '=ngModel',
            label: '@',
            protocols: '='
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
})
.filter('policy', function () {
    return function (input) {
        if(!input) {
            return 'N/A';
        }
    };
})
.filter('certificates', function () {
    return function (input) {
        if(!input) {
            return 'N/A';
        }
    };
});
