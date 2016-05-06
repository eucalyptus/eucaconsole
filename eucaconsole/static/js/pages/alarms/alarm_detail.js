angular.module('AlarmDetailPage', [
    'AlarmsComponents', 'EucaChosenModule', 'ChartAPIModule', 'ChartServiceModule',
    'AlarmServiceModule', 'AlarmActionsModule', 'ModalModule', 'CreateAlarmModal', 'EucaRoutes'
])
.directive('alarmDetail', ['eucaRoutes', function (eucaRoutes) {
    return {
        restrict: 'A',
        link: function (scope, element, attrs) {
            scope.alarm = JSON.parse(attrs.alarmDetail);
            scope.alarm.actions = scope.alarm.actions || [];
            scope.alarms = [scope.alarm];  // Delete alarm confirmation dialog expects a list of alarms
            scope.expanded = true;
            scope.alarmDimensions = scope.alarm.dimensions;  // Leveraged in delete alarm confirmation dialog
            // Need stringified form on details page (and Copy Alarm dialog) to set current dimension choice
            scope.alarm.dimensions = JSON.stringify(scope.alarm.dimensions);

            if (parseInt(attrs.invalidDimensions, 10) || 0) {
                // Handle when resource in dimensions is no longer available
                scope.alarm.dimensions = '';
            }

            eucaRoutes.getRouteDeferred('cloudwatch_alarms').then(function (path) {
                scope.redirectPath = path;
            });

            scope.$watchCollection('alarm.actions', function () {
                scope.collateActions();
            });
        },
        controller: ['$scope', '$window', 'AlarmService', 'ModalService',
        function ($scope, $window, AlarmService, ModalService) {
            var csrf_token = $('#csrf_token').val();

            $scope.saveChanges = function (event) {
                $scope.alarm.dimensions = JSON.parse($scope.alarm.dimensions);
                $scope.alarm.update = true;
                if($scope.alarmUpdateForm.$invalid || $scope.alarmUpdateForm.$pristine) {
                    var $error = $scope.alarmUpdateForm.$error;
                    Object.keys($error).forEach(function (error) {
                        $error[error].forEach(function (current) {
                            current.$setTouched();
                        });
                    });
                    return;
                }

                AlarmService.updateAlarm($scope.alarm, csrf_token, true)
                    .then(function success (response) {
                        $window.location.href = $scope.redirectPath;
                    }, function error (response) {
                        $window.location.href = $scope.redirectPath;
                    });
            };

            $scope.$on('actionsUpdated', function (event, actions) {
                $scope.alarmUpdateForm.$setDirty();
                var targets = {
                    ALARM: 'alarm_actions',
                    INSUFFICIENT_DATA: 'insufficient_data_actions',
                    OK: 'ok_actions'
                };
                $scope.alarm.insufficient_data_actions = [];
                $scope.alarm.alarm_actions = [];
                $scope.alarm.ok_actions = [];

                actions.forEach(function (action) {
                    var target = targets[action.alarm_state];
                    $scope.alarm[target].push(action.arn);
                });
            });

            $scope.$watch('alarm.threshold', function (newVal, oldVal) {
                if (newVal && newVal !== oldVal && !!oldVal) {
                    $scope.$broadcast('alarmThresholdChanged', {threshold: newVal, dimensions: $scope.alarm.dimensions});
                }
            });

            $scope.deleteAlarm = function (event) {
                event.preventDefault();

                var alarms = [{
                    name: $scope.alarm.name
                }];

                AlarmService.deleteAlarms(alarms, csrf_token, true)
                    .then(function success (response) {
                        $window.location.href = $scope.redirectPath;
                    }, function error (response) {
                        Notify.failure(response.data.message);
                    }); 
            };

            $scope.copyAlarm = function () {
                ModalService.openModal('copyAlarm');
            };

            $scope.collateActions = function () {
                var targets = {
                    ALARM: 'alarm_actions',
                    INSUFFICIENT_DATA: 'insufficient_data_actions',
                    OK: 'ok_actions'
                };
                $scope.alarm.insufficient_data_actions = [];
                $scope.alarm.alarm_actions = [];
                $scope.alarm.ok_actions = [];

                $scope.alarm.actions.forEach(function (action) {
                    var target = targets[action.alarm_state];
                    $scope.alarm[target].push(action.arn);
                });
            };
        }]
    };
}])
;
