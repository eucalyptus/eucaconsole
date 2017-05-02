angular.module('ReportingPage')
.controller('DashboardController', ['$scope', 'ReportingService', 'eucaHandleError',
    function ($scope, ReportingService, eucaHandleError) {
        var vm = this;
        vm.today = new Date();
        vm.monthToDateUsage = [];
        vm.loadRecentData = function() {
            // use reports service to load montly report data
            ReportingService.getRecentUsage().then(
            function success(result) {
                    vm.monthToDateUsage = result.results;
                },
                function error(errData) {
                    eucaHandleError(errData.data.message, errData.status);
                });
        };
        vm.loadRecentData();
    }
]);
