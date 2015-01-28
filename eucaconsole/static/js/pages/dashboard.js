/**
 * @fileOverview Dashboard JS
 * @requires AngularJS
 *
 */

angular.module('Dashboard', ['EucaConsoleUtils'])
    .controller('DashboardCtrl', function ($scope, $http, eucaUnescapeJson) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.jsonEndpoint = '';
        $scope.statusEndpoint = '';
        $scope.selectedZone = '';
        $scope.storedZoneKey = '';
        $scope.zoneDropdown = $('#zone-dropdown');
        $scope.itemsLoading = true;
        $scope.health = [];
        $scope.setInitialZone = function () {
            var storedZone = Modernizr.localstorage && localStorage.getItem($scope.storedZoneKey);
            $scope.selectedZone = storedZone || '';
        };
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.jsonEndpoint = options['json_items_url'];
            $scope.statusEndpoint = options['service_status_url'];
            $scope.storedZoneKey = 'dashboard_availability_zone_' + options['cloud_type'];
            $scope.accountName = options['account_display_name'];
            $scope.setInitialZone();
            $scope.setFocus();
            $scope.getItemCounts();
            $scope.storeAWSRegion();
            $scope.health = options['services'];
            var tiles = $.cookie($scope.accountName + "_dash_order");
            if (tiles == undefined || tiles.indexOf('health') > -1) {
                $scope.getServiceStatus();
            }
            $('#sortable').sortable({
                start: function (event, ui) {
                    ui.item.css({'z-index': '999999999'});
                },
                stop: function(event, ui) {
                    // TODO: remove 'add-tile' from list first
                    var order = $('#sortable').sortable('toArray');
                    var add_idx = order.indexOf('add-tile');
                    if (add_idx > -1) {
                        order.splice(add_idx, 1);
                    }
                    $.cookie($scope.accountName + "_dash_order", order, {expires: 180});
                }
            });
            $('#sortable').disableSelection();
            $('#new-tile').chosen({'width': '100%', search_contains: true});
            $('#add-tile-btn').on('click', $scope.addTile);
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
                $scope.setServiceStatus(results.health.name, results.health.status);
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
                
            });
        };
        $scope.getServiceStatus = function() {
            angular.forEach($scope.health, function(value, key) {
                if (key == 0) return;  // skip first, it's compute and that's fetch elsewhere
                var url = $scope.statusEndpoint+"?svc="+value.name.replace('&', '%26');
                $http.get(url).success(function(oData) {
                    var results = oData ? oData : {};
                    $scope.setServiceStatus(results.health.name, results.health.status);
                }).error(function (oData, status) {
                    var errorMsg = oData['message'] || null;
                    if (errorMsg && status === 403) {
                        $('#timed-out-modal').foundation('reveal', 'open');
                    }
                    
                });
            })
        };
        $scope.setServiceStatus = function(name, status) {
            angular.forEach($scope.health, function(value, key) {
                if (name == value.name) {
                    value.status = status;
                }
            });
        }
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
                localStorage.removeItem($scope.storedZoneKey);
                $scope.selectedZone = '';
            }
        };
        $scope.addTile = function() {
            var tile = $('#new-tile').val();
            var order = $('#sortable').sortable('toArray');
            var add_idx = order.indexOf('add-tile');
            if (add_idx > -1) {
                order.splice(add_idx, 1);
            }
            order.push(tile);
            $.cookie($scope.accountName + "_dash_order", order, {expires: 180});
            window.location.reload();
        };
        $scope.removeTile = function(tile) {
            var order = $('#sortable').sortable('toArray');
            var add_idx = order.indexOf('add-tile');
            if (add_idx > -1) {
                order.splice(add_idx, 1);
            }
            order.splice(order.indexOf(tile), 1);
            $.cookie($scope.accountName + "_dash_order", order, {expires: 180});
            window.location.reload();
        };
        $scope.resetTiles = function() {
            $.removeCookie($scope.accountName + "_dash_order");
            window.location.reload();
        };
    })
;
