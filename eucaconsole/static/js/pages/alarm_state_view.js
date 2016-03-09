angular.module('AlarmStateView', ['EucaRoutes', 'EucaConsoleUtils', 'AlarmServiceModule'])
    .directive('alarmStateView', function() {
        return {
            scope: {
                template: '@',
                resourceId: '@',
                resourceName: '@',
                resourceType: '@'
            },
            restrict: 'E',
            templateUrl: function (element, attributes) {
                return attributes.template;
            },
            controller: ['$scope', '$http', 'eucaRoutes', 'eucaHandleError', 'AlarmService', function($scope, $http, eucaRoutes, eucaHandleError, AlarmService) {
                $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
                $scope.alarms = [];
                $scope.toggleContent = function() {
                    $scope.expanded = !$scope.expanded;
                };
                eucaRoutes.promise.then(function() {
                    refreshList();
                });
                var refreshList = function() {
                    $scope.loading = true;
                    $http({method:'GET',
                        url: eucaRoutes.getRoute('cloudwatch_alarms_for_resource_json', {'id': $scope.resourceId}) + "?resource-type=InstanceId",
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                    }).then(function successCallback(oData) {
                        var response = oData.data ? oData.data : [];
                        $scope.alarms = response.results.sort(function(a, b) {
                            return a.name > b.name;
                        });
                        $scope.loading = false;
                    }, function errorCallback(errData) {
                        eucaHandleError(errData.data.message, errData.status);
                        $scope.loading = false;
                    });
                };
                $scope.showDeleteModal = function(alarm) {
                    $scope.alarmToDelete = alarm;
                    $('#remove-alarm-modal').foundation('reveal', 'open');
                };
                $scope.removeAlarm = function(event) {
                    $('#remove-alarm-modal').foundation('reveal', 'close');
                    $scope.toggleContent();
                    $scope.loading = true;
                    AlarmService.deleteAlarms([$scope.alarmToDelete], eucaRoutes.getRoute('cloudwatch_alarms'), $('#csrf_token').val())
                        .then(function success (response) {
                            Notify.success(response.data.message);
                            refreshList();
                        }, function error (response) {
                            Notify.failure(response.data.message);
                        }); 
                };
            }]
        };
    })
;
