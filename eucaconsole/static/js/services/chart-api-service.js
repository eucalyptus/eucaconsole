angular.module('ChartAPIModule', ['EucaConsoleUtils'])
.factory('CloudwatchAPI', ['$http', 'eucaHandleError', function ($http, eucaHandleError) {
    return {
        getChartData: function (params) {
            return $http({
                url: '/cloudwatch/api',
                method: 'GET',
                params: params
            }).then(function success (oData) {
                if (typeof oData === 'string' && oData.indexOf('<html') > -1) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
                return oData.data;
            }, function error (errorResponse) {
                eucaHandleError(
                    errorResponse.statusText,
                    errorResponse.status);
            });
        },

        getAlarmsForMetric: function (metricName, params) {
            return $http({
                url: '/alarms/json/' + metricName,
                method: 'GET',
                params: params
            }).then(function success (oData) {
                return oData.data.results;
            }, function error (errorResponse) {
                eucaHandleError(
                    errorResponse.statusText,
                    errorResponse.status);
            });
        }
    };
}]);
