angular.module('ELBWizard')
.controller('AdvancedController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    this.protocol = 'HTTP';
    this.port = 80;
    this.path = '/';
}]);

