/**
 * @fileOverview Images landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('ImagesPage', ['LandingPage', 'EucaConsoleUtils'])
    .controller('ImagesCtrl', function ($scope, $http, eucaUnescapeJson, handleError) {
        $scope.imageID = '';
        $scope.disabledExplanationVisible = false;
        $scope.snapshotImagesRegistered = [];
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.imagesUrl = options['snapshot_images_json_url'];
            $scope.imageCancelUrl = options['image_cancel_url'];
        };
        $scope.revealModal = function (action, image) {
            var modal = $('#' + action + '-image-modal');
            $scope.imageID = image['id'];
            $scope.imageNameID = image['name_id'];
            $scope.imageRootDeviceType = image['root_device_type'];
            $scope.imageSnapshotID = image['snapshot_id'];
            $scope.snapshotImagesRegistered = [];
            if (action == "deregister") {
                $scope.getSnapshotImages($scope.imageSnapshotID, $scope.imagesUrl);
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
                handleError(oData, status);
            });
        };
        $scope.cancelCreate = function ($event, item) {
            var url = $scope.imageCancelUrl.replace('_id_', item.fake_id);
            var data = "csrf_token="+$('#csrf_token').val();
            $http({method:'POST', url:url, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                // could put data back into form, but form already contains changes
                if (oData.error == undefined) {
                    Notify.success(oData.message);
                } else {
                    Notify.failure(oData.message);
                }
              }).
              error(function (oData, status) {
                handleError(oData, status);
              });
        };
    })
;

