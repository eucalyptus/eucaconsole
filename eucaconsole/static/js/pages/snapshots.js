/**
 * @fileOverview Snapshots landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('SnapshotsPage', ['LandingPage'])
    .controller('SnapshotsCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.snapshotID = '';
        $scope.snapshotName = '';
        $scope.imagesURL = '';
        $scope.images = undefined;
        $scope.initSnapshots = function (imagesURL) {
            $scope.imagesURL = imagesURL;
        };
        $scope.revealModal = function (action, snapshot) {
            var modal = $('#' + action + '-snapshot-modal');
            $scope.snapshotID = snapshot['id'];
            $scope.snapshotName = snapshot['name'];
            if (action == "delete") {
                $scope.images = undefined;
                $scope.getSnapshotImages(snapshot, $scope.imagesURL);
            }
            modal.foundation('reveal', 'open');
        };
        $scope.getSnapshotImages = function (snapshot, url) {
            url = url.replace('_id_', snapshot.id);
            $http.get(url).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results && results.length > 0) {
                    $scope.images = results;
                }
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
            });
        };
    })
;

