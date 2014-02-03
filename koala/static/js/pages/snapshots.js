/**
 * @fileOverview Snapshots landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('SnapshotsPage', ['LandingPage'])
    .controller('SnapshotsCtrl', function ($scope) {
        $scope.snapshotID = '';
        $scope.revealModal = function (action, snapshot_id) {
            var modal = $('#' + action + '-snapshot-modal');
            $scope.snapshotID = snapshot_id;
            modal.foundation('reveal', 'open');
        };
    })
;

