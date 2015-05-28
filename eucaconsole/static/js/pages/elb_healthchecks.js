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
            $scope.pingProtocol = $('#ping_protocol').val();
            $scope.pingPath = $('#ping_path').val();
            if ($scope.pingProtocol === 'HTTP' || $scope.pingProtocol === 'HTTPS') {
                $scope.pingPathRequired = true;
            }
        };
        $scope.setWatch = function () {
            eucaHandleUnsavedChanges($scope);
            $scope.$watch('pingProtocol', function () {
                $scope.updatePingPath();
            });
            $(document).on('input', 'input', function () {
                $scope.isNotChanged = false;
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
