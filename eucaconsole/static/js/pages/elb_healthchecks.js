/**
 * @fileOverview ELB Health Checks Page JS
 * @requires AngularJS
 *
 */

angular.module('ELBHealthChecksPage', ['EucaConsoleUtils'])
    .controller('ELBHealthChecksPageCtrl', function ($scope, eucaHandleUnsavedChanges) {
        $scope.isNotChanged = true;
        $scope.initController = function () {
            $scope.setWatch();
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
                $scope.pingPath = 'None';
            } else if ($scope.pingProtocol === 'HTTP' || $scope.pingProtocol === 'HTTPS') {
                if ($scope.pingPath === 'None') {
                    $scope.pingPath = '';
                }
            }
        };
    })
;
