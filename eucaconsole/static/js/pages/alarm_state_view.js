angular.module('AlarmStateView', ['EucaRoutes', 'EucaConsoleUtils'])
    .directive('alarmStateView', function() {
        return {
            scope: {
                template: '@',
                resourceId: '='
            },
            restrict: 'E',
            templateUrl: function (element, attributes) {
                return attributes.template;
            },
            controller: ['$scope', '$http', 'eucaRoutes', 'eucaHandleError', function($scope, $http, eucaRoutes, eucaHandleError) {
                $scope.alarms = [];
                $scope.toggleContent = function() {
                    $scope.expanded = !$scope.expanded;
                };
                $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
                var csrf_token = $('input[name="csrf_token"]').val();
                var data = "&csrf_token=" + csrf_token;
                $http({method:'POST', url: eucaRoutes.getRoute('alarms_for_resource', {'id': $scope.resourceId}),
                    data:data,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                }).then(function successCallback(oData) {
                    var response = oData.data ? oData.data : [];
                    $scope.alarms = response.alarms;
                }, function errorCallback(errData) {
                    eucaHandleError(errData.data.message, errData.status);
                });
            }]
        };
    })
;
