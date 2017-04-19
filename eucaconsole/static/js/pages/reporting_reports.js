angular.module('ReportingPage')
.controller('ReportsController', ['$scope', 'ReportingService', 'eucaHandleError', 'ModalService',
    function ($scope, ReportingService, eucaHandleError, ModalService) {
    var vm = this;
    vm.monthChoices = [];
    var month = new Date();
    // set earliest year/month to show in options list (remember Jan == 0)
    while (month.getFullYear() > 2017 || month.getMonth() >= 1) {
        vm.monthChoices.push(month);
        month = new Date(month.getFullYear(), month.getMonth()-1);
    }
    vm.monthlyUsage = [{details:'ec2 instances', total:'4'}, {details:'volumes', total:'5'}];
    vm.values = {
        monthSelection: vm.monthChoices[0],
    };
    vm.loadingUsageData = false;
    vm.showUsageReportsByService = function() {
        ModalService.openModal('usageReports');
    };
    vm.loadMonthlyData = function() {
        // use reports service to load montly report data
        vm.loadingUsageData = true;
        ReportingService.getMonthlyUsage(vm.values.monthSelection.getFullYear(),
            (vm.values.monthSelection.getMonth() + 1)).then(
        function success(result) {
                vm.monthlyUsage = result.results;
                vm.loadingUsageData = false;
            },
            function error(errData) {
                eucaHandleError(errData.data.message, errData.status);
                vm.loadingUsageData = false;
            });
    };
    vm.loadMonthlyData();
    vm.downloadCSV = function() {
        // use reports service to get montly data in csv format
        var url = '/reporting-api/monthlyusage?year=' + vm.values.monthSelection.getFullYear() +
                  '&month=' +  (vm.values.monthSelection.getMonth() + 1);
        $.generateFile({
            csrf_token: $('#csrf_token').val(),
            filename: 'not-used', // let the server set this
            content: 'none',
            script: url
        });
    };
}]);
