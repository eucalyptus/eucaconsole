angular.module('TagEditorModule', ['EucaConsoleUtils'])
    .directive('tagEditor', ['eucaUnescapeJson', function (eucaUnescapeJson) {
        return {
            scope: {
                template: '@',
                showNameTag: '@'
            },
            transclude: true,
            restrict: 'E',
            require: 'ngModel',
            templateUrl: function (element, attributes) {
                return attributes.template;
            },
            controller: ['$scope', function ($scope) {
                $scope.addTag = function () {
                    if(!$scope.tagForm.$valid) {
                        return
                    }

                    $scope.tags.push({
                        name: $scope.newTagKey,
                        value: $scope.newTagValue,
                        propagate_at_launch: !!$scope.newTagPropagate
                    });

                    $scope.newTagKey = '';
                    $scope.newTagValue = '';
                    $scope.newTagPropagate= false;
                    $scope.tagForm.key.$setPristine();
                    $scope.tagForm.key.$setUntouched();
                    $scope.tagForm.value.$setPristine();
                    $scope.tagForm.value.$setUntouched();
                    $scope.tagForm.$setPristine();
                    $scope.tagForm.$setUntouched();
                };

                $scope.removeTag = function ($index) {
                    $scope.tags.splice($index, 1);
                };
            }],
            link: function (scope, element, attrs, ctrl, transcludeContents) {
                var content = transcludeContents();
                scope.tags = JSON.parse(content.text() || '{}');

                if(!attrs.showNameTag) {
                    attrs.showNameTag = true;
                }

                scope.updateViewValue = function () {
                    ctrl.$setViewValue(scope.tags);
                };
                ctrl.$setViewValue(scope.tags);
            }
        };
    }])
    .directive('tagName', function () {
        var validPattern = /^(?!aws:)(?!euca:).{0,128}$/;
        return {
            require: 'ngModel',
            link: function (scope, element, attrs, ctrl) {
                ctrl.$validators.tagName = function (modelValue, viewValue) {
                    return validPattern.test(viewValue);
                };
            }
        };
    })
    .directive('tagValue', function () {
        var validPattern = /^(?!aws:).{0,256}$/;
        return {
            require: 'ngModel',
            link: function (scope, element, attrs, ctrl) {
                ctrl.$validators.tagValue = function (modelValue, viewValue) {
                    return validPattern.test(viewValue);
                };
            }
        };
    })
    .filter('ellipsis', function () {
        return function (line, num) {
            if (line.length <= num) {
                return line;
            }
            return line.substring(0, num) + "...";
        };
    })
    .filter('safe', ['$sanitize', function ($sanitize) {
        return function (tag) {
            return $sanitize(tag.name + ' = ' + tag.value);
        };
    }]);