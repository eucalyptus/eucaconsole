/**
 * @fileOverview ELB Health Checks Page JS
 * @requires AngularJS
 *
 */

angular.module('ELBHealthChecksPage', ['EucaConsoleUtils'])
    .controller('ELBHealthChecksPageCtrl', function ($scope, eucaHandleUnsavedChanges) {
        $scope.isNotChanged = true;
        $scope.pingPathRequired = false;
        $scope.initController = function () {
            $scope.setInitialValues();
            $scope.setWatch();
        };
        $scope.setInitialValues = function () {
            var originalPingPort = parseInt($('#ping_port').val() || 80, 10);
            var originalProtocol = $('#ping_protocol').val();
            $scope.originalPingProtocol = originalProtocol;
            $scope.pingProtocol = originalProtocol;
            $scope.originalPingPort = originalPingPort;
            $scope.pingPort = originalPingPort;
            $scope.pingPath = $('#ping_path').val();
            if ($scope.pingProtocol === 'HTTP' || $scope.pingProtocol === 'HTTPS') {
                $scope.pingPathRequired = true;
            }
        };
        $scope.setWatch = function () {
            eucaHandleUnsavedChanges($scope);
            $scope.$watch('pingProtocol', function (newVal) {
                $scope.updatePingPort(newVal);
                $scope.updatePingPath();
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
            // Look up original protocol/port values to avoid wiping out set value when selecting protocol
            var protocolPortMapping = {
                'HTTP': $scope.originalPingProtocol === 'HTTP'? $scope.originalPingPort : 80,
                'HTTPS': $scope.originalPingProtocol === 'HTTPS'? $scope.originalPingPort : 443,
                'SSL': $scope.originalPingProtocol === 'SSL'? $scope.originalPingPort :  443,
                'TCP': $scope.originalPingProtocol === 'TCP'? $scope.originalPingPort : 25
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
