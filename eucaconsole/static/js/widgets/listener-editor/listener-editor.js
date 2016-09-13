angular.module('ELBListenerEditorModule', [])
.directive('listenerEditor', function () {
    var protocols = [
        {'name': 'HTTP', 'value': 'HTTP', 'port': 80},
        {'name': 'HTTPS', 'value': 'HTTPS', 'port': 443},
        {'name': 'TCP', 'value': 'TCP', 'port': 80},
        {'name': 'SSL', 'value': 'SSL', 'port': 443}
    ];

    return {
        restrict: 'E',
        scope: {
            'listeners': '=ngModel'
        },
        templateUrl: '/_template/elbs/listener-editor/listener-editor',
        controller: ['$scope', function ($scope) {
            var vm = this;

            this.protocols = protocols;

            this.onUpdate = function (protocol) {
                $scope.port = protocol.port;
            };
        }],
        controllerAs: 'ctrl'
    };
})
.directive('protocolPort', function () {
    return {
        require: '^listenerEditor'
    };
})
.directive('validListener', function () {
    return {
        require: '^listenerEditor'
    };
});
