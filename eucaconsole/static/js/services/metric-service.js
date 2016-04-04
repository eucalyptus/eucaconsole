angular.module('MetricServiceModule', ['EucaRoutes'])
.factory('MetricService', ['$http', 'eucaRoutes', function ($http, eucaRoutes) {
    var _metrics = {};

    return {
        getMetrics: function (type, value) {
            if(value in _metrics) {
                return _metrics[value];
            }
            return eucaRoutes.getRouteDeferred('metrics_available_for_resource', {type: type, value: value})
                .then(function (path) {
                    return $http({
                        method: 'GET',
                        url: path
                    }).then(function (result) {
                        if(result && result.data) {
                            _metrics[value] = result.data.metrics;
                        }
                        return _metrics[value];
                    });
                });
        }
    };
}]);
