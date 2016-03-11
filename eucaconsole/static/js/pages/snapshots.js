/**
 * @fileOverview Snapshots landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('SnapshotsPage', ['LandingPage', 'EucaConsoleUtils', 'smart-table'])
    .controller('SnapshotsCtrl', function ($scope, $http, eucaHandleError) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.snapshotID = '';
        $scope.snapshotName = '';
        $scope.imagesURL = '';
        $scope.images = [];
        $scope.multipleItemsSelected = false;
        $scope.initSnapshots = function (imagesURL) {
            $scope.imagesURL = imagesURL;
        };
        $scope.revealModal = function (action, snapshot) {
            var modal = $('#' + action + '-snapshot-modal');
            $scope.snapshotID = snapshot.id;
            $scope.snapshotName = snapshot.name;
            if (action === "delete") {
                $scope.images = [];
                $scope.getSnapshotImages(snapshot, $scope.imagesURL);
            }
            modal.foundation('reveal', 'open');
        };
        $scope.revealMultiSelectModal = function (action, selectedItems) {
            var modal = $('#' + action + '-snapshot-modal'),
                snapshotIDs = [],
                snapshotNames = [];
            selectedItems.forEach(function (item) {
                snapshotIDs.push(item.id);
                snapshotNames.push(item.name || item.id);
            });
            if (action === "delete") {
                $scope.images = [];
                selectedItems.forEach(function (snapshot) {
                    $scope.getSnapshotImages(snapshot, $scope.imagesURL);
                });
            }
            $scope.multipleItemsSelected = snapshotIDs.length > 1;
            $scope.snapshotID = snapshotIDs.join(', ');
            $scope.snapshotName = snapshotNames.join(', ');
            modal.foundation('reveal', 'open');
        };
        $scope.getSnapshotImages = function (snapshot, url) {
            url = url.replace('_id_', snapshot.id);
            $http.get(url).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results && results.length > 0) {
                    $scope.images.push.apply($scope.images, results);
                }
            }).error(function (oData, status) {
                eucaHandleError(oData, status);
            });
        };
    })
;

