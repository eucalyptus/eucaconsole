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

            var validPorts = [25, 80, 443, 465, 587],
                validPortMin = 1024,
                validPortMax = 65535;

            this.protocols = [
                {name: 'Select...', value: 'None', port: ''},
                {name: 'HTTP', value: 'HTTP', port: 80},
                {name: 'HTTPS', value: 'HTTPS', port: 443},
                {name: 'TCP', value: 'TCP', port: 80},
                {name: 'SSL', value: 'SSL', port: 443}
            ];

            this.sourceValid = function (source) {
                var validPort = !this.portInUse(source) && !this.portOutOfRange(source);
                var validProtocol = source.protocol !== 'None';

                return (validPort && validProtocol);
            };

            this.targetValid = function (target) {
                var port = Number(target.port);
                var validPort = (port >= 1) && (port <= validPortMax);

                return validPort && target.protocol !== 'None';
            };

            this.portsValid = function () {
                var fromValid = this.sourceValid(vm.from);
                var toValid = this.targetValid(vm.to);

                return fromValid && toValid;
            };

            this.portInUse = function (target) {
                var usedPorts = $scope.listeners.map(function (item) {
                    return item.fromPort;
                });
                return usedPorts.some(function (current) {
                    return Number(target.port) === current;
                });
            };

            this.portOutOfRange = function (target, allowEmpty) {
                if(target.port === undefined && allowEmpty) {
                    return false;
                }

                var port = Number(target.port);
                var validReservedPort = validPorts.some(function (current) {
                    return current === port;
                });
                var validUnreservedPort = (port >= validPortMin) && (port <= validPortMax);

                return !(validReservedPort || validUnreservedPort);
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
            //  Custon form-field behavior. Let protocol-port act as a form field.

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

                ctrl.$setTouched();
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
