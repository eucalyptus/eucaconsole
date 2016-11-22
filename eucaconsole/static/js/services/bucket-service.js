/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview factory methods for S3 bucket XHR calls
 * @requires AngularJS
 *
 */
angular.module('BucketServiceModule', [])
.factory('BucketService', ['$http', '$interpolate', function ($http, $interpolate) {
    $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    return {
        getBuckets: function (csrfToken) {
            return $http({
                method: 'POST',
                url: '/buckets/json',
                data: 'csrf_token=' + csrfToken,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }).then(function success (response) {
                var data = response.data || {
                    results: []
                };
                return data.results;
            });
        },
        createBucket: function (bucketName, csrfToken) {
            formData = {
                'csrf_token': csrfToken,
                'bucket_name': bucketName
            };
            return $http({
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                method: 'POST',
                url: '/buckets/create_xhr',
                data: $.param(formData)
            });
        }
    };
}]);
