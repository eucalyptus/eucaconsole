
angular.module('EucaRoutes', [])
.service('eucaRoutes', function($http, $interpolate) {
    var routes = null;
    var promise = $http.get('/static/json/routes.json').then(
        function successCallback(data) {
            routes = data.data;
        },
        function errorCallback() {
            console.log("error fetching routes!");
        }
    );
    return {
        promise: promise,
        getRoute: function(routeName, params) {
            var ret = routes[routeName];
            if (params !== undefined) {
                ret = $interpolate(ret)(params);
            }
            return ret;
        },
        getRouteDeferred: function (routeName, params) {
            var getRoute = this.getRoute;
            return promise.then(function () {
                return getRoute(routeName, params);
            });
        }
    };
});
