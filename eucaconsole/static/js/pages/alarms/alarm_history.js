angular.module('AlarmHistoryPage', ['MagicSearch', 'AlarmServiceModule', 'ModalModule'])
.config(['$compileProvider', '$locationProvider', function ($compileProvider, $locationProvider) {
    var whitelist = /^\s*(https?|ftp|mailto|tel|file|data):/;
    $compileProvider.aHrefSanitizationWhitelist(whitelist);

    $locationProvider.html5Mode({enabled:true, requireBase:false, rewriteLinks:false });
}])
.directive('alarmHistory', function () {
    return {
        compile: function (tElement, tAttrs) {
            var alarm = JSON.parse(tAttrs.alarmHistory);

            return function (scope, element, attrs) {
                scope.alarmId = attrs.alarmId;
                scope.historicEvents = alarm;
                scope.unfilteredEvents = angular.copy(scope.historicEvents);
                scope.facetFilteredEvents = scope.unfilteredEvents;
                scope.searchFilter = '';

                scope.$on('searchUpdated', scope.searchUpdatedHandler);
                scope.$on('textSearch', scope.textSearchHandler);
            };
        },
        controller: ['$scope', '$timeout', '$location', 'AlarmService', 'ModalService',
        function ($scope, $timeout, $location, AlarmService, ModalService) {
            $scope.textSearchHandler = function (event, filterText) {
                $scope.searchFilter = filterText.toLowerCase();
                $scope.textFilterEvents();
            };
            $scope.textFilterEvents = function() {
                if($scope.searchFilter === '') {
                    $timeout(function() {
                        $scope.historicEvents = $scope.facetFilteredEvents;
                    });
                    return;
                }

                $scope.historicEvents = $scope.facetFilteredEvents.filter(function (item) {
                    return item.HistorySummary.toLowerCase().indexOf($scope.searchFilter) !== -1;
                });
                $scope.$apply();
            };

            $scope.searchUpdatedHandler = function (event, query) {
                // update url
                var url = window.location.href;
                if (url.indexOf("?") > -1) {
                    url = url.split("?")[0];
                }
                if (query.length > 0) {
                    url = url + "?" + query;
                }
                $location.search(query);
                window.history.pushState(null, "", $location.absUrl());
                $scope.facetFilterItems();
            };
            $scope.facetFilterItems = function() {
                var query = '';
                var url = window.location.href;
                if (url.indexOf("?") > -1) {
                    query = url.split("?")[1];
                }
                if (query === '') {
                    $scope.facetFilteredEvents = $scope.unfilteredEvents;
                    $scope.textFilterEvents();
                    return;
                }

                var facets = {};
                query.split('&').forEach(function (item) {
                    var q = item.split('=');
                    var field = q.shift(),
                        value = q.shift();

                    if(!(field in facets)) {
                        facets[field] = [];
                    }
                    facets[field].push(value);
                });

                $scope.facetFilteredEvents = $scope.unfilteredEvents.filter(function (item) {
                    return Object.keys(facets).some(function (key) {
                        return facets[key].some(function (value) {
                            return item[key] == value;
                        });
                    });
                });
                $scope.textFilterEvents();
            };

            $scope.getItems = function () {
                AlarmService.getHistory($scope.alarmId).then(function (items) {
                    $scope.historicEvents = items;
                    $scope.itemsLoading = false;
                    $scope.facetFilterItems();
                });
            };

            $scope.showDetails = function (item) {
                $scope.currentHistoryItem = item;
                ModalService.openModal('historyItemDetails');
            };
        }]
    };
})
.directive('alarmHistoryDetails', function () {
    return {
        restrict: 'A',
        require: '^modal',
        link: function (scope, element, attrs) {
            scope.detailDisplayJson = JSON.stringify(
                scope.currentHistoryItem, null, 2);
            scope.downloadableContent = btoa(scope.detailDisplayJson);

            var target = element.find('pre');
            scope.highlightContents(target[0]);

            scope.$on('modal:close', function () {
                delete scope.currentHistoryItem;
                delete scope.downloadableContent;
            });
        },
        controller: ['$scope', function ($scope) {
            $scope.highlightContents = function (element) {
                var range = document.createRange();
                range.selectNodeContents(element);

                var selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
            };
        }]
    };
});
