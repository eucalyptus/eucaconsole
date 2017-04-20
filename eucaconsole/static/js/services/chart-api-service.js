/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview factory method for chart XHR call
 * @requires AngularJS, jQuery
 *
 */
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
    };
}]);
