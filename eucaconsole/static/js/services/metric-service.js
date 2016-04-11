angular.module('MetricServiceModule', ['EucaRoutes'])
.factory('MetricService', ['$http', 'eucaRoutes', function ($http, eucaRoutes) {
    var _metrics = {};

    return {
        getMetrics: function (namespace, type, value) {
            if(value in _metrics) {
                return _metrics[value];
            }
            return eucaRoutes.getRouteDeferred('metrics_available_for_resource', {type: type, value: value})
                .then(function (path) {
                    return $http({
                        method: 'GET',
                        url: path + '?namespace=' + namespace
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
