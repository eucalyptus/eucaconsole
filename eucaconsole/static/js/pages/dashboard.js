/**
 * @fileOverview Dashboard JS
 * @requires AngularJS
 *
 */

angular.module('Dashboard', [])
    .controller('DashboardCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.jsonEndpoint = '';
        $scope.selectedZone = '';
        $scope.storedZoneKey = '';
        $scope.zoneDropdown = $('#zone-dropdown');
        $scope.itemsLoading = true;
        $scope.setInitialZone = function () {
            var storedZone = Modernizr.localstorage && localStorage.getItem($scope.storedZoneKey);
            $scope.selectedZone = storedZone || '';
        };
        $scope.initController = function (jsonItemsEndpoint, cloud_type) {
            $scope.jsonEndpoint = jsonItemsEndpoint;
            $scope.storedZoneKey = 'dashboard_availability_zone_'+cloud_type;
            $scope.setInitialZone();
            $scope.setFocus();
            $scope.getItemCounts();
            $scope.storeAWSRegion();
        };
        $scope.setFocus = function() {
            $('#zone-selector').find('a').get(0).focus();
        };
        $scope.getItemCounts = function() {
            var jsonUrl = $scope.jsonEndpoint;
            if ($scope.selectedZone) {
                jsonUrl += '?zone=' + $scope.selectedZone;
            }
            $http.get(jsonUrl).success(function(oData) {
                var results = oData ? oData : {};
                $scope.itemsLoading = false;
                $scope.totals = results;
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
            });
        };
        $scope.setZone = function (zone) {
            $scope.itemsLoading = true;
            $scope.selectedZone = zone;
            Modernizr.localstorage && localStorage.setItem($scope.storedZoneKey, zone);
            $scope.zoneDropdown.removeClass('open').removeAttr('style');
            $scope.getItemCounts();
        };
        $scope.storeAWSRegion = function () {
            if ($('#region-dropdown').length > 0 && Modernizr.localstorage) {
                localStorage.setItem('aws-region', $('#region-dropdown').children('li[data-selected="True"]').children('a').attr('id'));
            }
        };
    })
;
