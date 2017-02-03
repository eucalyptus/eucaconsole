/**
 * Copyright 2017 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Route Table Editor directive
 * @requires AngularJS
 *
 */
angular.module('RouteTableEditorModule', [])
    .factory('RouteTargetService', ['$http', '$interpolate', function ($http, $interpolate) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        return {
            getRouteTargets: function (vpcId) {
                return $http({
                    method: 'GET',
                    url: $interpolate('/vpcs/{{vpcId}}/route-targets-json')({vpcId: vpcId})
                }).then(function success (response) {
                    var data = response.data || {
                        results: []
                    };
                    return data.results;
                });
            }
        };
    }])
    .directive('routeTableEditor', function (RouteTargetService) {
        return {
            scope: {
                vpcId: '@'
            },
            transclude: true,
            restrict: 'E',
            require: 'ngModel',
            templateUrl: '/_template/vpcs/route-table-editor',
            controller: function ($scope) {
                $scope.destinationCidrBlock = '';
                $scope.routeTarget = '';
                $scope.routeTargets = [];
                $scope.routesUpdated = false;
                $scope.routeTargetsLoading = true;

                $scope.$watch('destinationCidrBlock', requireOther('routeTarget'));
                $scope.$watch('routeTarget', requireOther('destinationCidrBlock'));

                RouteTargetService.getRouteTargets($scope.vpcId).then(function (results) {
                    $scope.routeTargets = results;
                    $scope.routeTargetsLoading = false;
                });

                function requireOther (other) {
                    return function (newVal) {
                        if(newVal === '' || $scope[other] === '') {
                            $scope.routeTableForm.$setPristine();
                        }
                    };
                }

                $scope.addRoute = function ($event) {
                    $event.preventDefault();

                    // Don't add route if either CIDR block or route target is empty
                    if ($scope.destinationCidrBlock === '' || $scope.routeTarget === '') {
                        return;
                    }
                    if ($scope.routeTableForm.$invalid || $scope.routeTableForm.$pristine) {
                        return;
                    }

                    // Avoid adding route that conflicts with another destination CIDR block
                    var existingCidrBlocks = $scope.routes.map(function (route) {
                        return route.destination_cidr_block;
                    });
                    if (existingCidrBlocks.indexOf($scope.destinationCidrBlock) !== -1) {
                        return;
                    }

                    var route = {
                        destination_cidr_block: $scope.destinationCidrBlock,
                        state: 'active'
                    };

                    if ($scope.routeTarget.indexOf('igw-') === 0) {
                        route.gateway_id = $scope.routeTarget;
                    } else if ($scope.routeTarget.indexOf('eni-') === 0) {
                        route.interface_id = $scope.routeTarget;
                    }

                    $scope.routes.push(route);
                    $scope.routesUpdated = true;
                    resetForm();
                };

                $scope.removeRoute = function ($index) {
                    $scope.routes.splice($index, 1);
                    $scope.routesUpdated = true;
                };

                var resetForm = function () {
                    $scope.destinationCidrBlock = '';
                    $scope.routeTarget = '';
                    $scope.routeTableForm.$setPristine();
                    $scope.routeTableForm.$setUntouched();
                };

            },
            link: function (scope, element, attrs, ctrl, transcludeContents) {
                var content = transcludeContents();
                scope.routes = JSON.parse(content.text() || '[]');
                scope.cidrPattern = attrs.cidrPattern;

                scope.updateViewValue = function () {
                    ctrl.$setViewValue(scope.routes);
                };
                ctrl.$setViewValue(scope.routes);
            }
        };
    });
