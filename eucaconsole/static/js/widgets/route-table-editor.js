/**
 * Copyright 2017 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Route Table Editor directive
 * @requires AngularJS
 *
 */
angular.module('RouteTableEditorModule', ['RouteTargetServiceModule'])
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

                    if ($scope.destinationCidrBlock === '' || $scope.routeTarget === '') {
                        return;
                    }

                    if ($scope.routeTableForm.$invalid || $scope.routeTableForm.$pristine) {
                        return;
                    }

                    var route = {
                        destination_cidr_block: $scope.destinationCidrBlock,
                        state: 'active',
                        // TODO: Set interface_id instead if ENI selected
                        gateway_id: $scope.routeTarget
                    };

                    $scope.routes.push(route);
                    resetForm();
                    $scope.$emit('routeTableUpdated');
                };

                $scope.removeRoute = function ($index) {
                    $scope.routes.splice($index, 1);
                    $scope.$emit('routeTableUpdated');
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
