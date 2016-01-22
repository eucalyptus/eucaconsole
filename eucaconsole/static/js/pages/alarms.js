/**
 * @fileOverview CloudWatch Alarms landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('AlarmsPage', ['LandingPage', 'CreateAlarm'])
    .controller('AlarmsCtrl', ['$scope', '$timeout', function ($scope, $timeout) {
        $scope.alarmID = '';
        $scope.revealModal = function (action, item) {
            var modal = $('#' + action + '-alarm-modal');
            if(item) {
                $scope.alarmID = item.id;
            }
            modal.foundation('reveal', 'open');
        };

        $scope.$on('alarm_created', function ($event, promise) {
            promise.then(function success (result) {
                //
                //  NEVER DO THIS!!  THIS IS TERRIBLE!!!
                //  The proper solution, which will be implemented soon,
                //  is to have this and the parent controllers attached
                //  to directives, thus enabling cross-controller communication
                //  via ng-require.
                //
                //  But, this will do for now.
                //
                $timeout(function () {
                    $('#refresh-btn').click();
                });
            });
        });
    }])
    .directive('alarmState', function () {
        var stateValues = {
            'OK': 'Ok',
            'ALARM': 'Alarm',
            'INSUFFICIENT_DATA': 'Insufficient data'
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
