/**
 * @fileOverview CloudWatch Alarms landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('AlarmsPage', [
    'LandingPage', 'AlarmsComponents', 'AlarmServiceModule', 'ChartAPIModule',  'ChartServiceModule',
    'CustomFilters', 'CreateAlarmModal', 'ModalModule'
])
    .controller('AlarmsCtrl', ['$scope', '$timeout', 'AlarmService', 'ModalService', function ($scope, $timeout, AlarmService, ModalService) {
        $scope.alarms = [];
        $scope.selectedAlarm = null;
        var csrf_token = $('#csrf_token').val();

        this.revealModal = function (action, item) {
            $scope.alarms = [].concat(item);

            $scope.expanded = false;
            if(action === 'delete' && $scope.alarms.length === 1) {
                $scope.expanded = true;
            }

            var modal = $('#' + action + '-alarm-modal');
            modal.foundation('reveal', 'open');
        };

        $scope.toggleContent = function() {
            $scope.expanded = !$scope.expanded;
        };

        $scope.deleteAlarm = function (event) {
            $('#delete-alarm-modal').foundation('reveal', 'close');

            AlarmService.deleteAlarms($scope.alarms, csrf_token)
                .then(function success (response) {
                    Notify.success(response.data.message);
                    $scope.refreshList();
                }, function error (response) {
                    Notify.failure(response.data.message);
                }); 
        };

        $scope.$on('alarmStateView:refreshList', function () {
            $scope.refreshList();
        });

        $scope.refreshList = function () {
            // TODO: Better refresh event handling
            $timeout(function () {
                $('#refresh-btn').click();
            });
        };

        $scope.$on('alarm_created', function ($event, promise) {
            promise.then(function success (result) {
                $scope.refreshList();
            });
        });

        this.showCopyAlarm = function(alarm) {
            $scope.selectedAlarm = alarm;
            $timeout(function() {
                ModalService.openModal('copyAlarm');
            });
        };

    }]);
