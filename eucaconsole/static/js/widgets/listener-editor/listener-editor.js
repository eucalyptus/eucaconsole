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

            this.from = this.protocols[0];
            this.to = this.protocols[0];
            this.certificate = {};
            this.backendCertificates = [];

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
                if(target.port === '' && allowEmpty) {
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
                    fromProtocol: vm.from.value,
                    toPort: vm.to.port,
                    toProtocol: vm.to.value,
                    certificate: vm.certificate,
                    backendCertificates: vm.backendCertificates
                };
                $scope.listeners.push(listener);

                vm.reset();
            };

            this.reset = function () {
                vm.from = vm.protocols[0];
                vm.to = vm.protocols[0];
                vm.certificate = {};
                vm.backendCertificates = [];
            };
            this.cancel = this.reset;

            this.openCertificateModal = function () {
                ModalService.openModal('certificateEditor');
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
        return input;
    };
});
