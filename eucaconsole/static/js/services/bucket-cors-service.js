/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview factory methods for S3 bucket CORS config XHR calls
 * @requires AngularJS, jQuery
 *
 */
angular.module('CorsServiceModule', ['EucaRoutes'])
.factory('CorsService', ['$http', 'eucaRoutes', function ($http, eucaRoutes) {
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

    return {
        setCorsConfig: function (name, csrfToken, corsConfigXml) {
            return eucaRoutes.getRouteDeferred('bucket_set_cors_configuration', { name: name })
                .then(function (path) {
                    return $http({
                        method: 'PUT',
                        url: path,
                        data: {
                            csrf_token: csrfToken,
                            cors_configuration_xml: corsConfigXml
                        }
                    });
                });
        }

    };
}]);
