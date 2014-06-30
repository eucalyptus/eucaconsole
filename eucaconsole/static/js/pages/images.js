/**
 * @fileOverview Images landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('ImagesPage', ['LandingPage'])
    .controller('ImagesCtrl', function ($scope, $http) {
        $scope.imageID = '';
        $scope.disabledExplanationVisible = false;
        $scope.snapshotImagesRegistered = [];
        $scope.initSnapshotImages = function (imagesURL) {
            $scope.imagesURL = imagesURL;
        };
        $scope.revealModal = function (action, image) {
            var modal = $('#' + action + '-image-modal');
            $scope.imageID = image['id'];
            $scope.imageNameID = image['name_id'];
            $scope.imageRootDeviceType = image['root_device_type'];
            $scope.imageSnapshotID = image['snapshot_id'];
            $scope.snapshotImagesRegistered = [];
            if (action == "deregister") {
                $scope.getSnapshotImages($scope.imageSnapshotID, $scope.imagesURL);
            }
            modal.foundation('reveal', 'open');
            var form = $('#deregister-form');
            var formAction = form.attr('action').replace("_id_", image['id']);
            form.attr('action', formAction);
        };
        $scope.getSnapshotImages = function (snapshot_id, url) {
            url = url.replace('_id_', snapshot_id);
            $http.get(url).success(function(oData) {
                $scope.snapshotImagesRegistered = oData ? oData.results : [];
                $(document).foundation('tooltip');
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
            });
        };
    })
;

