angular.module('ReportingPage')
.controller('DashboardController', ['$scope', 'ReportingService', 'eucaHandleError',
    function ($scope, ReportingService, eucaHandleError) {
        var vm = this;
        vm.today = new Date();
        vm.monthToDateUsage = [];
        vm.loadMonthToDateData = function() {
            // use reports service to load montly report data
            ReportingService.getMonthToDateUsage(vm.today.getFullYear(), vm.today.getMonth()+1).then(
            function success(result) {
                    vm.monthToDateUsage = result.results;
                },
                function error(errData) {
                    eucaHandleError(errData.data.message, errData.status);
                });
        };
        vm.loadMonthToDateData();
    }
]);
