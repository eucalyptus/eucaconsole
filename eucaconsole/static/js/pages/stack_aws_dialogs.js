/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview directive to show aws warning dialogs
 * @requires AngularJS, jQuery
 *
 */
angular.module('StackAWSDialogs', ['EucaConsoleUtils'])
    .directive('awsTemplateDialogs', function (eucaUnescapeJson) {
        return {
            scope: {
                template: '@',
                serviceList: '=',
                resourceList: '=',
                propertyList: '=',
                parameterList: '=',
                parameters: '=',
                paramModels: '=',
                loading: '=',
                checkRequiredInput: '&'
            },
            restrict: 'E',
            templateUrl: function (element, attributes) {
                return attributes.template;
            },
            controller: ['$scope', '$http', 'eucaHandleError', function($scope, $http, eucaHandleError) {
                $scope.toggleContent = function () {
                    $scope.expanded = !$scope.expanded;
                };
                $scope.convertTemplate = function () {
                    var fd = new FormData();
                    // fill from actual form
                    angular.forEach($('form').serializeArray(), function(value, key) {
                        this.append(value.name, value.value);
                    }, fd);
                    // skip file param since we're relying on template already being in S3
                    $scope.loading = true;
                    $scope.parameters = undefined;
                    $http.post('/stacks/templateconvert', fd, {
                            headers: {'Content-Type': undefined},
                            transformRequest: angular.identity
                    }).
                    success(function(oData) {
                        var results = oData ? oData.results : '';
                        if (results) {
                            $scope.loading = false;
                            $('#aws-warn-modal').foundation('reveal', 'close');
                            $scope.s3TemplateKey = results.template_key;
                            $scope.parameters = results.parameters;
                            if ($scope.parameters !== undefined) {
                                angular.forEach($scope.parameters, function(param, idx) {
                                    if (param.default !== undefined) {
                                        $scope.paramModels[param.name] = param.default;
                                    }
                                });
                            }
                            $scope.checkRequiredInput();
                        }
                    }).
                    error(function (oData, status) {
                        $scope.loading = false;
                        eucaHandleError(oData, status);
                    });
                };
            }]
        };
    })
;
