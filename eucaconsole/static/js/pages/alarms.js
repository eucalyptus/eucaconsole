/**
 * @fileOverview CloudWatch Alarms landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('AlarmsPage', ['LandingPage'])
    .controller('AlarmsCtrl', function ($scope) {
        $scope.alarmID = '';
        $scope.revealModal = function (action, item) {
            var modal = $('#' + action + '-alarm-modal');
            $scope.alarmID = item.id;
            modal.foundation('reveal', 'open');
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
