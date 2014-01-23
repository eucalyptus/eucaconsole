/**
 * @fileOverview Dashboard JS
 * @requires AngularJS
 *
 */

angular.module('Dashboard', [])
    .controller('DashboardCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.getItemCounts = function(jsonEndpoint) {
            $scope.itemsLoading = true;
            $http.get(jsonEndpoint).success(function(oData) {
                console.log(status)
                var results = oData ? oData : {};
                $scope.itemsLoading = false;
                $scope.totals = results;
            }).error(function (oData, status) {
                var errorMsg = oData['error'] || null;
                if (errorMsg && status === 403) {
                    alert(errorMsg);
                    $('#euca-logout-form').submit();
                }
            });
        };
    })
;
