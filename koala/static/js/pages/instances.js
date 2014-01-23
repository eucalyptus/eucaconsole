/**
 * @fileOverview Instances landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('InstancesPage', ['CustomFilters'])
    .controller('InstancesCtrl', function ($scope) {
        $scope.instanceID = '';
        $scope.urlParams = $.url().param();
        $scope.displayType = $scope.urlParams['display'] || 'gridview';
        $scope.revealModal = function (action, instance) {
            var modal = $('#' + action + '-instance-modal');
            $scope.instanceID = instance['id'];
            $scope.rootDevice = instance['root_device'];
            modal.foundation('reveal', 'open');
        };
    })
    .controller('ItemsCtrl', function ($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.items = [];
        $scope.unfilteredItems = [];
        $scope.sortBy = '';
        $scope.jsonEndpoint = '';
        $scope.searchFilter = '';
        $scope.itemsLoading = true;
        $scope.setInitialSort = function (sortKey) {
            $scope.sortBy = sortKey;
            $scope.$watch('sortBy',  function () { 
                if ($('#sorting-dropdown').hasClass('open')) { 
                    $('#sorting-dropdown').removeClass('open'); 
                    $('#sorting-dropdown').removeAttr('style'); 
                } 
            });
        };
        $scope.initController = function (sortKey, jsonItemsEndpoint) {
            $scope.jsonEndpoint = jsonItemsEndpoint;
            $scope.setInitialSort(sortKey);
            $scope.getItems();
        };
        $scope.getItems = function () {
            $http.get($scope.jsonEndpoint).success(function(oData) {
                var results = oData ? oData.results : [];
                var transitionalCount = 0;
                $scope.itemsLoading = false;
                $scope.items = results;
                $scope.unfilteredItems = results;
                $scope.items.forEach(function (item) {
                    if (item['transitional']) {
                        transitionalCount += 1;
                    }
                });
                // Auto-refresh instances if any of them are in progress
                if (transitionalCount > 0) {
                    $timeout(function() { $scope.getItems(); }, 5000);  // Poll every 5 seconds
                }
            });
        };
        /*  Filter items client side based on search criteria.
         *  @param {array} filterProps Array of properties to filter items on
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

