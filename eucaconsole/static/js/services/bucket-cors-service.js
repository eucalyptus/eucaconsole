/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview factory methods for S3 bucket CORS config XHR calls
 * @requires AngularJS
 *
 */
angular.module('CorsServiceModule', [])
.factory('CorsService', ['$http', function ($http) {
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

    return {
        setCorsConfig: function (bucketName, csrfToken, corsConfigXml) {
            return $http({
                method: 'PUT',
                url: '/buckets/' + bucketName + '/cors_configuration',
                data: {
                    csrf_token: csrfToken,
                    cors_configuration_xml: corsConfigXml
                }
            });
        },

        deleteCorsConfig: function (bucketName, csrfToken) {
            return $http({
                method: 'DELETE',
                url: '/buckets/' + bucketName + '/cors_configuration',
                params: {
                    csrf_token: csrfToken
                }
            });
        }
   };
}]);
