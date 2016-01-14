angular.module('AlarmsComponents', [])
    .directive('alarmState', function () {
        var stateValues = {
            'OK': 'ok',
            'ALARM': 'alarm',
            'INSUFFICIENT_DATA': 'insufficient data'
        };
        var stateClasses = {
            'OK': 'success',
            'ALARM': 'alert',
            'INSUFFICIENT_DATA': 'secondary'
        };
        return {
            restrict: 'A',
            scope: {
                alarmState: '@'
            },
            template: '<span class="label status radius" ng-class="alarmClass()">{{ stateDisplay }}</span>',
            controller: function ($scope) {
                var alarmState = $scope.alarmState || 'INSUFFICIENT_DATA';
                $scope.stateDisplay = stateValues[alarmState];

                $scope.alarmClass = function () {
                    return stateClasses[alarmState];
                };
            }
        };
    })
    .directive('dimensions', function () {
        return {
            restrict: 'A',
            scope: {
                dimensions: '@'
            },
            template: '<dt ng-repeat-start="item in flattened_dimensions">{{ item.key }}</dt><dd ng-repeat-end="">{{ item.value }}</dd>',
            controller: function ($scope, $element, $attrs) {
                var dimensions = JSON.parse($scope.dimensions);
                $scope.flattened_dimensions = [];

                Object.keys(dimensions).forEach(function (currentKey) {
                    var dimension = dimensions[currentKey];
                    dimension.forEach(function (currentValue) {
                        $scope.flattened_dimensions.push({
                            key: currentKey,
                            value: currentValue
                        });
                    });
                });
            }
        };
    });
