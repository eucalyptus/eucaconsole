/**
 * @fileOverview Image Picker JS
 * @requires AngularJS
 *
 */
angular.module('ImagePicker', [])
    .controller('ImagePickerCtrl', function ($scope, $http) {
        $scope.items = [];
        $scope.batchSize = 100;  // Show 100 items max w/o "show more" enabler
        $scope.ownerAlias = '';
        $scope.jsonURL = '';
        $scope.initImagePicker = function (jsonEndpoint) {
            $scope.jsonURL = jsonEndpoint;
            if ($scope.jsonURL) {
                $scope.getItems();
            }
        };
        $scope.getItems = function () {
            if ($scope.ownerAlias) {
                $scope.jsonURL += '?owner_alias=' + $scope.ownerAlias;
            }
            $scope.itemsLoading = true;
            $http.get($scope.jsonURL).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = false;
                $scope.items = results;
                $scope.unfilteredItems = results;
            });
        };
    })
;
