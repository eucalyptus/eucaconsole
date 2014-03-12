/**
 * @fileOverview Volume Snapshots page JS
 * @requires AngularJS
 *
 */

angular.module('VolumeSnapshots', ['TagEditor'])
    .controller('VolumeSnapshotsCtrl', function ($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.loading = false;
        $scope.snapshots = [];
        $scope.jsonEndpoint = '';
        $scope.initialLoading = true;
        $scope.deleteFormAction = '';
        $scope.initController = function (jsonEndpoint) {
            $scope.jsonEndpoint = jsonEndpoint;
            $scope.getVolumeSnapshots();
            $scope.setFocus();
            $scope.setDropdownMenusListener();
        };
        $scope.revealDeleteModal = function (action) {
            var modal = $('#delete-snapshot-modal');
            $scope.deleteFormAction = action;
            modal.foundation('reveal', 'open');
        };
        $scope.setFocus = function () {
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var inputElement = modal.find('input[type!=hidden]').get(0);
                var modalButton = modal.find('button').get(0);
                if (!!inputElement) {
                    inputElement.focus();
                } else if (!!modalButton) {
                    modalButton.focus();
                }
            });
        };
        $scope.setDropdownMenusListener = function () {
            var modals = $('[data-reveal]');
            modals.on('open', function () {
                $('.gridwrapper').find('.f-dropdown').filter('.open').css('display', 'none');
            });
            modals.on('close', function () {
                $('.gridwrapper').find('.f-dropdown').filter('.open').css('display', 'block');
            })
        };
        $scope.getVolumeSnapshots = function () {
            $http.get($scope.jsonEndpoint).success(function(oData) {
                var inProgressCount = 0;
                $scope.snapshots = oData ? oData.results : [];
                $scope.initialLoading = false;
                // Detect if any snapshots are in progress
                $scope.snapshots.forEach(function(snapshot) {
                    var progress = parseInt(snapshot.progress.replace('%', ''), 10);
                    if (progress < 100) {
                        inProgressCount += 1;
                    }
                });
                // Auto-refresh snapshots if any of them are in progress
                if (inProgressCount > 0) {
                    $timeout(function() { $scope.getVolumeSnapshots(); }, 4000);  // Poll every 4 seconds
                }
            }).error(function (oData, status) {
                var errorMsg = oData['error'] || null;
                if (errorMsg && status === 403) {
                    alert(errorMsg);
                    $('#euca-logout-form').submit();
                }
            });
        };
    })
;

