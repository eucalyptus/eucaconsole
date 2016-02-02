/**
 * @fileOverview CloudWatch Alarms landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('AlarmsPage', ['LandingPage', 'CustomFilters'])
    .controller('AlarmsCtrl', ['$scope', '$timeout', '$compile', 'AlarmService',
    function ($scope, $timeout, $compile, AlarmService) {
        $scope.alarms = [];


        $scope.revealModal = function (action, item) {
            $scope.alarms = [].concat(item);
            $scope.deleteAlarmsExpanded = false;

            var modal = $('#' + action + '-alarm-modal');
            modal.foundation('reveal', 'open');
        };

        $scope.deleteAlarm = function (event) {
            var servicePath = event.target.dataset.servicePath;
            $('#delete-alarm-modal').foundation('reveal', 'close');

            AlarmService.deleteAlarms($scope.alarms, servicePath).then(function success (response) {
                Notify.success(response.data.message);
                $scope.refreshList();
            }, function error (response) {
                Notify.failure(response.data.message);
            }); 
        };

        $scope.refreshList = function () {
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
        };

        $scope.toggleAlarmsDisplay = function () {
            $scope.deleteAlarmsExpanded = !$scope.deleteAlarmsExpanded;
        };

        $scope.$on('alarm_created', function ($event, promise) {
            promise.then(function success (result) {
                $scope.refreshList();
            });
        });
    }])
    .factory('AlarmService', ['$http', function ($http) {
        return {
            deleteAlarms: function (alarms, path) {
                var alarmNames = alarms.map(function (current) {
                    return current.name;
                });

                return $http({
                    method: 'DELETE',
                    url: path,
                    data: {
                        alarms: alarmNames
                    }
                });
            }
        };
    }])
    .directive('alarmState', function () {
        var stateValues = {
            'OK': 'OK',
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
