/**
 * @fileOverview ELB Health Checks Page JS
 * @requires AngularJS
 *
 */

angular.module('ELBHealthChecksPage', [])
    .controller('ELBHealthChecksPageCtrl', function ($scope) {
        $scope.isNotChanged = true;
        $scope.initController = function () {
            $scope.setWatch();
        };
        $scope.setWatch = function () {
            $scope.$watch('pingProtocol', function () {
                $scope.updatePingPath();
            });
            $scope.$watch('isNotChanged', function () {
                if ($scope.isNotChanged === false) {
                    $('#elb-view-tabs').removeAttr('data-tab');
                } else {
                    $('#elb-view-tabs').attr('data-tab', '');
                }
            });
            $(document).on('input', '#health-checks-tab input', function () {
                $scope.isNotChanged = false;
                $scope.$apply();
            });
            $(document).on('change', '#health-checks-tab select', function () {
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
