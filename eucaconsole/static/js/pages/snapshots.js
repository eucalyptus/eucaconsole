/**
 * @fileOverview Snapshots landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('SnapshotsPage', ['LandingPage'])
    .controller('SnapshotsCtrl', function ($scope) {
        $scope.snapshotID = '';
        $scope.snapshotName = '';
        $scope.revealModal = function (action, snapshot) {
            var modal = $('#' + action + '-snapshot-modal');
            $scope.snapshotID = snapshot['id'];
            $scope.snapshotName = snapshot['name'];
            modal.foundation('reveal', 'open');
        };
    })
;

