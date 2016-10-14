/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview directive to show cancel stack update dialog
 * @requires AngularJS, jQuery
 *
 */
angular.module('StackCancelUpdateDialog', ['EucaConsoleUtils'])
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
            controller: ['$scope', '$http', '$timeout', 'eucaHandleError', function($scope, $http, $timeout, eucaHandleError) {
                $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
                $scope.cancelUpdateStack = function($event) {
                    $event.preventDefault();
                    var csrf_token = $('input[name="csrf_token"]').val();
                    var data = "name=" + $scope.stackName + "&csrf_token=" + csrf_token;
                    $http({method:'POST', url: '/stacks/' + $scope.stackName + '/cancelupdate',
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
