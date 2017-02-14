/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Usage Reports JS
 * @requires AngularJS and jQuery
 *
 */
angular.module('UsageReportsModule', ['ModalModule', 'EucaConsoleUtils'])
.directive('datepicker', function () {
    return {
        require: 'ngModel',
        restrict: 'A',
        scope: {
            format: "@",
        },
        link: function(scope, element, attrs){
            if(typeof(scope.format) == "undefined"){ scope.format = "yyyy/mm/dd"; }
            var endDate = new Date();
            $(element).fdatepicker({format: scope.format, pickTime: false, endDate:endDate}).on('changeDate', function(ev){
                scope.$apply(function() {
                    ngModel.$setViewValue(ev.date);
                });
            });
        }
    }; 
})
.directive('usageReportsDialog', function() {
    return {
        restrict: 'A',
        templateUrl: '/_template/reporting/usage_reports',
        controller: ['$scope', '$http', '$httpParamSerializer', '$timeout', 'eucaHandleError', 'ModalService',
            function ($scope, $http, $httpParamSerializer, $timeout, eucaHandleError, ModalService) {
                var vm = this;
                vm.values = {
                    service: 'ec2',
                    usageType: 'all',
                    granularity: 'Hours',
                    timePeriod: 'lastWeek',
                    fromDate: '',
                    toDate: ''
                };
                vm.updateUsageType = function() {
                    vm.values.usageType = 'requests';
                    if (vm.values.service == 'ec2' || vm.values.service == 's3') {
                        vm.values.usageType = 'all';
                    }
                };
                vm.isDownloading = false;
                vm.downloadCSV = function ($event) {
                    $event.preventDefault();
                    if ($scope.downloadReportForm.$invalid) {
                        return false;
                    }
                    vm.isDownloading = true;
                    var params = {
                        'service': vm.values.service,
                        'usageType': vm.values.usageType,
                        'granularity': vm.values.granularity,
                        'timePeriod': vm.values.timePeriod,
                        'fromTime': vm.values.fromTime,
                        'toTime': vm.values.toTime,
                    };
                    var url = '/reporting-api/serviceusage?' + $httpParamSerializer(params);
                    $.generateFile({
                        csrf_token: $('#csrf_token').val(),
                        filename: 'not-used', // let the server set this
                        content: 'none',
                        script: url
                    });
                    $timeout(function() {
                        ModalService.closeModal('usageReports');
                    }, 3000);
                };
            }
        ],
        controllerAs: 'usagereports'
    };
});
