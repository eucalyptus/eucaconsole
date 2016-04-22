angular.module('AlarmHistoryPage', ['MagicSearch', 'AlarmServiceModule', 'ModalModule'])
.config(['$compileProvider', function ($compileProvider) {
    var whitelist = /^\s*(https?|ftp|mailto|tel|file|data):/;
    $compileProvider.aHrefSanitizationWhitelist(whitelist);
}])
.directive('alarmHistory', function () {
    return {
        link: function (scope, element, attrs) {
            scope.alarmId = attrs.alarmId;
            scope.historicEvents = JSON.parse(attrs.alarmHistory);
            scope.unfilteredEvents = angular.copy(scope.historicEvents);

            scope.$on('searchUpdated', scope.searchUpdatedHandler);
            scope.$on('textSearch', scope.textSearchHandler);
        },
        controller: ['$scope', 'AlarmService', 'ModalService',
        function ($scope, AlarmService, ModalService) {
            $scope.textSearchHandler = function (event, filterText) {
                if(filterText === '') {
                    $scope.historicEvents = $scope.unfilteredEvents;
                    return;
                }

                $scope.historicEvents = $scope.unfilteredEvents.filter(function (item) {
                    return item.history_item_type.toLowerCase() == filterText.toLowerCase();
                });
            };

            $scope.searchUpdatedHandler = function (event, query) {
                if(query === '') {
                    $scope.historicEvents = $scope.unfilteredEvents;
                    return;
                }

                var facets = {};
                query.split('&').forEach(function (item) {
                    var q = item.split('=');
                    var field = q.shift().toLowerCase(),
                        value = q.shift();

                    if(!(field in facets)) {
                        facets[field] = [];
                    }
                    facets[field].push(value);
                });

                $scope.historicEvents = $scope.unfilteredEvents.filter(function (item) {
                    return Object.keys(facets).some(function (key) {
                        return facets[key].some(function (value) {
                            return item[key] == value;
                        });
                    });
                });
            };

            $scope.getItems = function () {
                AlarmService.getHistory($scope.alarmId).then(function (items) {
                    $scope.historicEvents = items;
                    $scope.itemsLoading = false;
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
            scope.$on('modal:open', function (event, name) {
                scope.detailDisplayJson = JSON.stringify(
                    scope.currentHistoryItem, null, 2);
                scope.downloadableContent = btoa(scope.detailDisplayJson);

                var target = element.find('pre');
                scope.highlightContents(target[0]);
            });

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
