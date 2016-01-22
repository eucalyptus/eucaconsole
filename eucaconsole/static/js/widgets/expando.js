/**
 * @fileOverview expando table row directive
 * @requires AngularJS
 *
 */

angular.module('Expando', ['EucaConsoleUtils'])
    .directive('expando', function (eucaHandleError) {
        return {
            restrict: 'A',
            controller: ['$scope', '$http', '$timeout', function($scope, $http, $timeout) {
                $scope.expando = {};
                $scope.expando.loading = false;
                $scope.expando.data = undefined;
                $scope.toggle = function () {
                    if ($scope.expando.data !== undefined) {
                        $scope.expando.save = $scope.expando.data;
                        $scope.expando.data = undefined;
                        return;
                    }
                    if ($scope.expando.save !== undefined) {
                        $scope.expando.data = $scope.expando.save;
                        return;
                    }
                    if ($scope.url !== undefined) {
                        $scope.expando.loading = true;
                        $http.get($scope.url).then(function(response) {
                            var results = response.data ? response.data.results : '';
                            $scope.expando.loading = false;
                            if (results) {
                                $timeout(function() {
                                    $scope.expando.data = results;
                                });
                            }
                        },function(response) {
                            $scope.expando.loading = false;
                            eucaHandleError(response.statusText, response.status);
                        });
                    }
                    else {
                        $scope.expando.data = [];
                    }
                };
            }],
            link: function (scope, element, attrs, ctrl) {
                if (attrs.url !== undefined && attrs.url && attrs.itemId) {
                    scope.url = attrs.url.replace("__id__", attrs.itemId);
                }
            }
        };
    })
;
