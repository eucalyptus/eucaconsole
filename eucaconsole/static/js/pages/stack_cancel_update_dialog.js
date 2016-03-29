angular.module('StackCancelUpdateDialog', ['EucaRoutes', 'EucaConsoleUtils'])
    .directive('stackCancelUpdateDialog', function (eucaUnescapeJson) {
        return {
            scope: {
                template: '@',
                stackName: '='
            },
            restrict: 'E',
            templateUrl: function (element, attributes) {
                return attributes.template;
            },
            controller: ['$scope', '$http', '$timeout', 'eucaRoutes', 'eucaHandleError', function($scope, $http, $timeout, eucaRoutes, eucaHandleError) {
                $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
                $scope.cancelUpdateStack = function($event) {
                    $event.preventDefault();
                    var csrf_token = $('input[name="csrf_token"]').val();
                    var data = "name=" + $scope.stackName + "&csrf_token=" + csrf_token;
                    $http({method:'POST', url: eucaRoutes.getRoute('stack_cancel_update', {'name': $scope.stackName}),
                        data:data,
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                    }).then(function successCallback(oData) {
                        $('#cancel-update-stack-modal').foundation('reveal', 'close');
                        var response = oData.data ? oData.data : [];
                        if (response.error === undefined) {
                            $timeout(function() {
                                $scope.$broadcast('refresh');
                            }, 1000);
                            Notify.success(response.message);
                        } else {
                            Notify.failure(response.message);
                        }
                    }, function errorCallback(errData) {
                        $('#cancel-update-stack-modal').foundation('reveal', 'close');
                        eucaHandleError(errData.data.message, errData.status);
                    });
                };
            }]
        };
    })
;
