angular.module('RouteTableEditorModule', [])
    .directive('routeTableEditor', function () {
        return {
            scope: '=',
            transclude: true,
            restrict: 'E',
            require: 'ngModel',
            templateUrl: '/_template/vpcs/route-table-editor',
            controller: function ($scope) {
                $scope.addRoute = function ($event) {
                    $event.preventDefault();

                    var route = {
                        // TODO: Pull input values
                    };

                    $scope.routes.push(route);
                    $scope.$emit('routeTableUpdated');
                };

            },
            link: function (scope, element, attrs, ctrl, transcludeContents) {
                var content = transcludeContents();
                scope.routes = JSON.parse(content.text() || '[]');

                scope.updateViewValue = function () {
                    ctrl.$setViewValue(scope.routes);
                };
                ctrl.$setViewValue(scope.routes);
            }
        };
    });
