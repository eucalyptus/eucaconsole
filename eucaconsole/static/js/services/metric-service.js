/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview factory method for metric fetch XHR call
 * @requires AngularJS, jQuery
 *
 */
angular.module('MetricServiceModule', [])
.factory('MetricService', ['$http', function ($http) {
    return {
        getMetrics: function (namespace, dimensions) {
            return $http({
                method: 'GET',
                url: '/metrics/available/json',
                params: {namespace: namespace, dimensions: JSON.stringify(dimensions)}
            }).then(function (result) {
                var metrics = [],
                    namespaces = [];
                if(result && result.data) {
                    metrics = result.data.metrics || [];
                    namespaces = result.data.namespaces || [];
                }
                return {metrics: metrics, namespaces: namespaces};
            });
        }
    };
}]);
