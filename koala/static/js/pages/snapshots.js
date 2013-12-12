/**
 * @fileOverview Snapshots landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('SnapshotsPage', [])
    .controller('SnapshotsCtrl', function ($scope) {
        $scope.snapshotID = '';
        $scope.urlParams = $.url().param();
        $scope.displayType = $scope.urlParams['display'] || 'tableview';
        $scope.revealModal = function (action, snapshot_id) {
            var modal = $('#' + action + '-snapshot-modal');
            $scope.snapshotID = snapshot_id;
            modal.foundation('reveal', 'open');
        };
    })
    .controller('ItemsCtrl', function ($scope, $http) {
        $scope.items = [];
        $scope.unfilteredItems = [];
        $scope.sortBy = '';
        $scope.setInitialSort = function (sortKey) {
            $scope.sortBy = sortKey;
        };
        $scope.initController = function (sortKey, jsonItemsEndpoint) {
            $scope.setInitialSort(sortKey);
            $scope.getItems(jsonItemsEndpoint);
        };
        $scope.getItems = function (jsonItemsEndpoint) {
            // TODO: smart refresh
            $scope.itemsLoading = true;
            $http.get(jsonItemsEndpoint).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = false;
                $scope.items = results;
                $scope.unfilteredItems = results;
            });
        };
        /*  Filter items client side based on search criteria.
         *  @param {array} filterProps Array of properties to filter items on
         *  Note: We could potentially use Angular's template filter here, but it may be tricky to
         *        filter by nested properties.
         */
        $scope.searchFilterItems = function(filterProps) {
            $scope.items = $scope.unfilteredItems;  // reset prior to applying filter
            var filterText = ($scope.searchFilter || '').toLowerCase();
            // Leverage Array.prototype.filter (ECMAScript 5)
            var filteredItems = $scope.items.filter(function(item) {
                for (var i=0; i < filterProps.length; i++) {  // Can't use $.each or Array.prototype.forEach here
                    var propName = filterProps[i];
                    var itemProp = item.hasOwnProperty(propName) && item[propName];
                    if (itemProp && typeof itemProp === "string" && itemProp.toLowerCase().indexOf(filterText) !== -1) {
                        return item;
                    }
                }
            });
            $scope.items = filterText ? filteredItems : $scope.unfilteredItems;
        };
    })
;

