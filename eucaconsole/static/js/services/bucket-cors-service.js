/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview factory methods for S3 bucket CORS config XHR calls
 * @requires AngularJS
 *
 */
angular.module('CorsServiceModule', [])
.factory('CorsService', ['$http', '$interpolate', function ($http, $interpolate) {
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

    return {
        setCorsConfig: function (bucketName, csrfToken, corsConfigXml) {
            return $http({
                method: 'PUT',
                url: $interpolate('/buckets/{{name}}/cors_configuration')({name: bucketName}),
                data: {
                    csrf_token: csrfToken,
                    cors_configuration_xml: corsConfigXml
                }
            });
        },

        deleteCorsConfig: function (bucketName, csrfToken) {
            return $http({
                method: 'DELETE',
                url: $interpolate('/buckets/{{name}}/cors_configuration')({name: bucketName}),
                params: {
                    csrf_token: csrfToken
                }
            });
        }
   };
}]);
