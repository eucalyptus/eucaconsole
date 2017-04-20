/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview factory method for metric fetch XHR call
 * @requires AngularJS, jQuery
 *
 */
angular.module('MetricServiceModule', ['EucaRoutes'])
.factory('MetricService', ['$http', 'eucaRoutes', function ($http, eucaRoutes) {
    return {
        getMetrics: function (namespace, dimensions) {
            return eucaRoutes.getRouteDeferred('metrics_available_for_dimensions')
                .then(function (path) {
                    return $http({
                        method: 'GET',
                        url: path,
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
                });
        }
    };
}]);
