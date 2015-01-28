/**
 * @fileOverview Create Alarm JS
 * @requires AngularJS and jQuery
 *
 */
angular.module('CreateAlarm', ['EucaConsoleUtils'])
    .controller('CreateAlarmCtrl', function ($rootScope, $scope, $http, $timeout, eucaUnescapeJson) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.alarmDialog = $('#create-alarm-modal');
        $scope.createAlarmForm = $('#create-alarm-form');
        $scope.statisticField = $('#statistic');
        $scope.metricField = $('#metric');
        $scope.dimensionField = $('#dimension');
        $scope.metric = '';
        $scope.unitField = $('#unit');
        $scope.unitLabel = '';
        $scope.metricUnitMapping = {};
        $scope.isCreatingAlarm = false;
        $scope.existingAlarms = [];
        $scope.alarmName = '';
        $scope.existingAlarmConflict = false;
        $scope.setInitialValues = function () {
            $scope.metricField.val($scope.metricField.find('option[selected]').val());
            $scope.metricField.trigger('change');
        };
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.metricUnitMapping = options['metric_unit_mapping'];
            $scope.existingAlarms = options['existing_alarms'];
            $scope.alarmDialog.on('opened', function () {
                $scope.setInitialValues();
            });
            $scope.addListeners();
        };
        $scope.addListeners = function () {
            // Display notice if entered alarm name conflicts with existing alarm
            var alarmNameField = $scope.createAlarmForm.find('#name');
            alarmNameField.on('keyup blur', function () {
                var nameVal = $(this).val();
                $scope.$apply(function () {
                    $scope.existingAlarmConflict = ($scope.existingAlarms.indexOf(nameVal) > -1);
                });
            });
        };
        $scope.updateMetricNamespace = function () {
            var selectedOptionLabel = $scope.metricField.find('option[value="' + $scope.metric + '"]').text();
            $scope.namespace = selectedOptionLabel.split(' - ')[0];
            $timeout(function () {
                $scope.setUnitChoice();
                $scope.dimensionField.trigger('change');
            }, 50);
        };
        $scope.setUnitChoice = function () {
            var unitChoice = $scope.metricUnitMapping[$scope.metric];
            $scope.unitLabel = unitChoice && unitChoice.toLowerCase();
            if ($scope.unitLabel == 'none' || $scope.unitLabel == 'count') {
                $scope.unitLabel = '';
            }
            $scope.unitField.val(unitChoice);
        };
        $scope.handleCreateAlarm = function (postUrl, $event) {
            $event.preventDefault();
            var formData = $($event.target).serialize();
            $scope.createAlarmForm.trigger('validate');
            if ($scope.createAlarmForm.find('[data-invalid]').length) {
                return false;
            }
            $scope.isCreatingAlarm = true;
            $http({
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                method: 'POST',
                url: postUrl,
                data: formData
            }).success(function (oData) {
                // Add new alarm to choices and set it as selected
                var newAlarm = oData['new_alarm'];
                $rootScope.alarmChoices[newAlarm] = newAlarm;
                $rootScope.alarm = newAlarm;
                $scope.isCreatingAlarm = false;
                var modal = $scope.alarmDialog;
                modal.foundation('reveal', 'close');
            }).error(function (oData) {
                if (oData.message) {
                    Notify.failure(oData.message);
                    $scope.isCreatingAlarm = false;
                }
            });

        };
    })
;
