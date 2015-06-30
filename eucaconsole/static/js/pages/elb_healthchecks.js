/**
 * @fileOverview ELB Health Checks Page JS
 * @requires AngularJS
 *
 */

angular.module('ELBHealthChecksPage', ['EucaConsoleUtils'])
    .controller('ELBHealthChecksPageCtrl', function ($scope, eucaHandleUnsavedChanges, eucaUnescapeJson) {
        $scope.isNotChanged = true;
        $scope.pingPathRequired = false;
        $scope.loggingEnabled = false;
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.setInitialValues(options);
            $scope.setWatch();
        };
        $scope.setInitialValues = function (options) {
            $scope.pingProtocol = $('#ping_protocol').val();
            $scope.pingPort = parseInt($('#ping_port').val() || 80, 10);
            $scope.pingPath = $('#ping_path').val();
            if ($scope.pingProtocol === 'HTTP' || $scope.pingProtocol === 'HTTPS') {
                $scope.pingPathRequired = true;
            }
            $scope.loggingEnabled = options.logging_enabled;
        };
        $scope.setWatch = function () {
            eucaHandleUnsavedChanges($scope);
            $scope.$watch('pingProtocol', function (newVal) {
                $scope.updatePingPort(newVal);
                $scope.updatePingPath();
            });
            $scope.$watch('loggingEnabled', function (newVal, oldVal) {
                if (newVal !== oldVal) {
                    $scope.isNotChanged = false;
                }
            });
            $(document).on('input', 'input', function () {
                $scope.isNotChanged = false;
                $scope.$apply();
            });
            $(document).on('input', '#ping-path', function () {
                var field = $(this);
                var fieldWrapper = field.closest('.field');
                if (field.val()) {
                    fieldWrapper.removeClass('error');
                } else {
                    fieldWrapper.addClass('error');
                }
                $scope.$apply();
            });
            $(document).on('change', 'select', function () {
                $scope.isNotChanged = false;
                $scope.$apply();
            });
            // Leave button is clicked on the warning unsaved changes modal
            $(document).on('click', '#unsaved-changes-warning-modal-stay-button', function () {
                $('#unsaved-changes-warning-modal').foundation('reveal', 'close');
            });
            // Stay button is clicked on the warning unsaved changes modal
            $(document).on('click', '#unsaved-changes-warning-modal-leave-link', function () {
                $scope.unsavedChangesWarningModalLeaveCallback();
            });
        };
        $scope.updatePingPort = function (newVal) {
            var protocolPortMapping = {
                'HTTP': 80,
                'HTTPS': 443,
                'SSL': 443
            };
            if (!!protocolPortMapping[newVal]) {
                $scope.pingPort = protocolPortMapping[newVal];
            }
        };
        $scope.updatePingPath = function () {
            if ($scope.pingProtocol === 'TCP' || $scope.pingProtocol === 'SSL') {
                $scope.pingPathRequired = false;
                $scope.pingPath = 'None';
            } else if ($scope.pingProtocol === 'HTTP' || $scope.pingProtocol === 'HTTPS') {
                $scope.pingPathRequired = true;
                if ($scope.pingPath === 'None') {
                    $scope.pingPath = 'index.html';
                }
            }
        };
    })
;
