
angular.module('EucaRoutes', [])
.service('eucaRoutes', function($http) {
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
                // replace route variables
                params.forEach(function(param) {
                    ret = ret.replace("{"+param+"}", params[param]);
                });
            }
            return ret;
        }
    };
});
