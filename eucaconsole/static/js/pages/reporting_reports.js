angular.module('ReportingPage')
.controller('ReportsController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    var vm = this;
    vm.monthChoices = ['January 2017', 'December 2016', 'November 2016'];
    vm.monthlyUsage = [{details:'ec2 instances', total:'4'}, {details:'volumes', total:'5'}];
    vm.values = {
        monthSelection: vm.monthChoices[0],
    };
}]);
