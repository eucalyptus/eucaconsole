angular.module('ReportingPage')
.controller('ReportsController', ['$scope', '$routeParams', 'ReportingService', 'eucaHandleError', function ($scope, $routeParams, ReportingService, eucaHandleError) {
    var vm = this;
    vm.monthChoices = ['January 2017', 'December 2016', 'November 2016'];
    vm.monthlyUsage = [{details:'ec2 instances', total:'4'}, {details:'volumes', total:'5'}];
    vm.values = {
        monthSelection: vm.monthChoices[0],
    };
    vm.showEC2InstanceUsageReport = function() {
    };
    vm.showUsageReportsByService = function() {
    };
    vm.loadMonthlyData = function() {
        // use reports service to load montly report data
        ReportingService.getMonthlyUsage(2017, 1).then(
        function success(result) {
                vm.monthlyUsage = result.results;
            },
            function error(errData) {
                eucaHandleError(errData.data.message, errData.status);
            });
    };
    vm.loadMonthlyData();
    vm.downloadCSV = function() {
        // use reports service to get montly data in csv format
        // use generateFile in success method to present file for user to download
        // see user_view.js for an example
    };
}]);
