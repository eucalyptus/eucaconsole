/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview directive to show alarms for resource and allow deletion
 * @requires AngularJS, jQuery
 *
 */
angular.module('AlarmStateView', ['EucaRoutes', 'EucaConsoleUtils', 'AlarmServiceModule', 'AlarmsComponents'])
    .directive('alarmStateView', function() {
        return {
            scope: {
                template: '@',
                resourceId: '@',
                resourceName: '@',
                resourceType: '@',
                resourceTypeName: '@'
            },
            restrict: 'E',
            templateUrl: function (element, attributes) {
                return attributes.template;
            },
            controller: ['$scope', '$timeout', 'eucaHandleError', 'eucaRoutes', 'AlarmService',
            function($scope, $timeout, eucaHandleError, eucaRoutes, AlarmService) {
                $scope.alarms = undefined;  // default to undefined helps avoid errant display of 0 alarms before fetch starts
                $scope.toggleContent = function() {
                    $scope.expanded = !$scope.expanded;
                };

                var refreshList = function () {
                    $scope.loading = true;
                    AlarmService.getAlarmsForResource($scope.resourceId, $scope.resourceType)
                        .then(function success (alarms) {
                            $scope.alarms = alarms.sort(function (a, b) {
                                return a.name > b.name;
                            });
                            $scope.loading = false;
                        }, function error (response) {
                            eucaHandleError(errData.data.message, errData.status);
                            $scope.loading = false;
                        });
                };
                refreshList();

                $scope.$on('alarmStateView:refreshList', function () {
                    refreshList();
                });

                $scope.alarmDetailPath = function (alarmName) {
                    return eucaRoutes.getRoute('cloudwatch_alarm_view', { alarm_id: btoa(alarmName) });
                };

                $scope.showDeleteModal = function(alarm) {
                    $scope.alarmToDelete = alarm;
                    $('#delete-alarm-modal').foundation('reveal', 'open');
                    $timeout(function() {
                        $('.close-reveal-modal').focus();
                    }, 500);
                };
                $scope.removeAlarm = function(event) {
                    $('#delete-alarm-modal').foundation('reveal', 'close');
                    $scope.toggleContent();
                    $scope.loading = true;
                    AlarmService.deleteAlarms([$scope.alarmToDelete], $('#csrf_token').val())
                        .then(function success (response) {
                            Notify.success(response.data.message);
                            refreshList();
                        }, function error (response) {
                            Notify.failure(response.data.message);
                        }); 
                };
            }]
        };
    })
;
