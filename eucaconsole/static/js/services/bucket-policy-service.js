/**
 * Copyright 2017 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview factory methods for S3 bucket policy config XHR calls
 * @requires AngularJS
 *
 */
angular.module('BucketPolicyServiceModule', [])
.factory('BucketPolicyService', ['$http', '$interpolate', function ($http, $interpolate) {
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

    return {
        setBucketPolicy: function (bucketName, csrfToken, bucketPolicyJson) {
            return $http({
                method: 'PUT',
                url: $interpolate('/buckets/{{name}}/policy')({name: bucketName}),
                data: {
                    csrf_token: csrfToken,
                    bucket_policy_json: bucketPolicyJson
                }
            });
        },

        deleteBucketPolicy: function (bucketName, csrfToken) {
            return $http({
                method: 'DELETE',
                url: $interpolate('/buckets/{{name}}/policy')({name: bucketName}),
                params: {
                    csrf_token: csrfToken
                }
            });
        }
   };
}]);
