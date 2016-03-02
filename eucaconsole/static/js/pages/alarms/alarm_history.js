angular.module('AlarmHistoryPage', ['MagicSearch'])
.directive('alarmHistory', function () {
    return {
        link: function (scope, element, attrs) {
            scope.historicEvents = JSON.parse(attrs.alarmHistory);
            scope.unfilteredEvents = angular.copy(scope.historicEvents);

            scope.$on('searchUpdated', scope.searchUpdatedHandler);
            scope.$on('textSearch', scope.textSearchHandler);
        },
        controller: ['$scope', function ($scope) {
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

                var q = query.split('=');
                var field = q.shift().toLowerCase(),
                    value = q.shift();

                $scope.historicEvents = $scope.unfilteredEvents.filter(function (item) {
                    return item[field] == value;
                });
            };
        }]
    };
});
