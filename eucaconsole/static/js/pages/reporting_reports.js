angular.module('ReportingPage')
.controller('ReportsController', ['$scope', 'ReportingService', 'eucaHandleError', 'ModalService',
    function ($scope, ReportingService, eucaHandleError, ModalService) {
    var vm = this;
    vm.monthChoices = ['January 2017', 'December 2016', 'November 2016'];
    vm.monthlyUsage = [{details:'ec2 instances', total:'4'}, {details:'volumes', total:'5'}];
    vm.values = {
        monthSelection: vm.monthChoices[0],
    };
    vm.showEC2InstanceUsageReport = function() {
    };
    vm.showUsageReportsByService = function() {
        ModalService.openModal('usageReports');
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
        var url = '/reporting-api/monthlyusage?year=2017&month=1';
        $.generateFile({
            csrf_token: $('#csrf_token').val(),
            filename: 'not-used', // let the server set this
            content: 'none',
            script: url
        });
    };
}]);
