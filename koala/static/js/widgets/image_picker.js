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
        $scope.jsonEndpoint = '';
        $scope.itemsLoading = false;
        $scope.cloudType = 'euca';
        $scope.setInitialOwnerChoice = function () {
            if ($scope.cloudType == 'euca') {
                $scope.ownerAlias = ''
            } else {
                $scope.ownerAlias = 'amazon'
            }
        };
        $scope.initImagePicker = function (jsonEndpoint, cloudType) {
            $scope.jsonEndpoint = jsonEndpoint;
            $scope.cloudType = cloudType;
            $scope.setInitialOwnerChoice();
            $scope.getItems();
        };
        $scope.getItems = function () {
            $scope.itemsLoading = true;
            var jsonURL = $scope.jsonEndpoint;
            if ($scope.ownerAlias) {
               jsonURL += '?owner_alias=' + $scope.ownerAlias;
            }
            $http.get(jsonURL).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = false;
                $scope.items = results;
                $scope.unfilteredItems = results;
            });
        };
    })
;
