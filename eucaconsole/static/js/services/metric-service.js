angular.module('MetricServiceModule', ['EucaRoutes'])
.factory('MetricService', ['$http', 'eucaRoutes', function ($http, eucaRoutes) {
    return {
        getMetrics: function (namespace, type, value) {
            return eucaRoutes.getRouteDeferred('metrics_available_for_resource', {type: type, value: value})
                .then(function (path) {
                    return $http({
                        method: 'GET',
                        url: path,
                        params: {namespace: namespace}
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
