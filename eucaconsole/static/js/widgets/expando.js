/**
 * @fileOverview expando table row directive
 * @requires AngularJS
 *
 */

angular.module('Expando', [])
    .directive('expando', function () {
        return {
            restrict: 'A',
            controller: ['$scope', '$http', '$timeout', function($scope, $http, $timeout) {
                $scope.expando = {};
                $scope.expando.loading = false;
                $scope.expando.data = undefined;
                $scope.toggle = function () {
                    if ($scope.expando.data !== undefined) {
                        $scope.expando.data = undefined;
                        return;
                    }
                    $scope.expando.loading = true;
                    $http.get($scope.url).success(function(oData) {
                        var results = oData ? oData.results : '';
                        $scope.expando.loading = false;
                        if (results) {
                            $timeout(function() {
                                $scope.expando.data = results;
                            });
                        }
                    }).error(function() {
                        $scope.expando.loading = false;
                    });
                };
            }],
            link: function (scope, element, attrs, ctrl) {
                if(attrs.url && attrs.activityId) {
                    scope.url = attrs.url.replace("__id__", attrs.activityId);
                }
            }
        };
    })
;
