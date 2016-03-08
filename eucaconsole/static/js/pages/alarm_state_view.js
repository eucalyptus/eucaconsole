angular.module('AlarmStateView', ['EucaConsoleUtils'])
    .directive('alarmStateView', function(eucaUnescapeJson) {
        return {
            scope: {
                template: '@'
            },
            restrict: 'E',
            templateUrl: function (element, attributes) {
                return attributes.template;
            },
            controller: ['$scope', '$http', 'eucaHandleError', function($scope, $http, eucaRoutes, eucaHandleError) {
                $scope.alarms = [];
                $scope.toggleContent = function() {
                    $scope.expanded = !$scope.expanded;
                };
            }]
        };
    })
;
