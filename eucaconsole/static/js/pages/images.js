/**
 * @fileOverview Images landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('ImagesPage', ['LandingPage', 'EucaConsoleUtils'])
    .controller('ImagesCtrl', function ($scope, $http, $q, eucaUnescapeJson, eucaHandleError) {
        $scope.imageID = '';
        $scope.disabledExplanationVisible = false;
        $scope.snapshotImagesRegistered = [];
        $scope.multipleItemsSelected = false;
        $scope.ebsImageIDs = [];
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.imagesUrl = options.snapshot_images_json_url;
            $scope.imageCancelUrl = options.image_cancel_url;
            $scope.cloudType = options.cloud_type;
            if ($scope.cloudType == 'aws') {
                $scope.setInitialOwner();
            }
        };
        $scope.setInitialOwner = function () {
            // Set "owned by Amazon" as default filter if on AWS
            $(document).ready(function () {
                if (document.URL.indexOf('owner_alias') === -1) {
                    $('select[name="owner_alias"]').find('option[value="amazon"]').prop('selected', true);
                }
            });
        };
        $scope.revealModal = function (action, image) {
            var modal = $('#' + action + '-image-modal');
            $scope.imageID = image.id;
            $scope.imageNameID = image.name_id;
            $scope.imageRootDeviceType = image.root_device_type;
            $scope.imageSnapshotID = image.snapshot_id;
            $scope.snapshotImagesRegistered = [];
            if (action === "deregister") {
                $scope.getSnapshotImages($scope.imageSnapshotID, $scope.imagesUrl);
            }
            modal.foundation('reveal', 'open');
            var form = $('#deregister-form');
            var formAction = form.attr('action').replace("_id_", image.id);
            form.attr('action', formAction);
        };
        $scope.revealMultiSelectDeregisterModal = function (selectedItems) {
            $scope.snapshotImagesRegistered = [];
            var modal = $('#deregister-image-modal'),
                itemIDs = [],
                itemNames = [],
                ebsImageIDs = [],
                snapshotIDs = [],
                snapshotImagesRegistered = [],
                apiPromises = [];
            selectedItems.forEach(function (item) {
                itemIDs.push(item.id);
                itemNames.push(item.name_id);
                if (item.root_device_type === 'ebs') {
                    ebsImageIDs.push(item.id);
                    if (snapshotIDs.indexOf(item.snapshot_id) === -1) {
                       snapshotIDs.push(item.snapshot_id);
                    }
                }
            });
            snapshotIDs.forEach(function (snapshotId) {
                var url = $scope.imagesUrl;
                var promise = $http.get(url.replace('_id_', snapshotId)); // Fetch images registered for snapshot
                apiPromises.push(promise);
            });
            // Wait for all API calls for snapshot Images registered to complete before setting scope variables
            $q.all(apiPromises).then(function(combinedResults) {
                combinedResults.forEach(function(oData) {
                    // NOTE: $q.all hoists results in a data attribute on completion, so use oData.data.results
                    //       instead of the usual oData.results
                    Array.prototype.push.apply(snapshotImagesRegistered, oData.data.results);
                });
                $scope.snapshotImagesRegistered = snapshotImagesRegistered;
                $scope.multipleItemsSelected = itemIDs.length > 1;
                $scope.imageID = itemIDs.join(', ');
                $scope.imageNameID = itemNames.join(', ');
                $scope.ebsImageIDs = ebsImageIDs;
                modal.foundation('reveal', 'open');
            }).catch(function(oData, status) {
                eucaHandleError(oData, status);
            });
        };
        $scope.getSnapshotImages = function (snapshot_id, url) {
            url = url.replace('_id_', snapshot_id);
            $http.get(url).success(function(oData) {
                $scope.snapshotImagesRegistered = oData ? oData.results : [];
                $(document).foundation('tooltip');
            }).error(function (oData, status) {
                eucaHandleError(oData, status);
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
                if (oData.error === undefined) {
                    Notify.success(oData.message);
                } else {
                    Notify.failure(oData.message);
                }
              }).
              error(function (oData, status) {
                eucaHandleError(oData, status);
              });
        };
    })
;

