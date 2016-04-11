angular.module('MetricServiceModule', ['EucaRoutes'])
.factory('MetricService', ['$http', 'eucaRoutes', function ($http, eucaRoutes) {
    var _metrics = {};

    return {
        getMetrics: function (namespace, type, value) {
            if(value in _metrics) {
                return _metrics[value];
            }
            var urlParams = {
                type: type,
                value: value,
                namespace: namespace  // Pass multiple namespaces as comma-separated list
            };
            return eucaRoutes.getRouteDeferred('metrics_available_for_resource', urlParams)
                .then(function (path) {
                    return $http({
                        method: 'GET',
                        url: path
                    }).then(function (result) {
                        var metrics;
                        if(result && result.data) {
                            metrics = result.data.metrics || [];
                            _metrics[value] = metrics;
                        }
                        return _metrics[value];
                    });
                });
        }
    };
}]);
