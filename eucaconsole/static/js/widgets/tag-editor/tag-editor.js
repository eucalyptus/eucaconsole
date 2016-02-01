angular.module('TagEditorModule', ['EucaConsoleUtils'])
    .directive('tagEditor', ['eucaUnescapeJson', function (eucaUnescapeJson) {
        return {
            scope: {
                template: '@',
                showNameTag: '@',
                autoscale: '@'
            },
            transclude: true,
            restrict: 'E',
            require: 'ngModel',
            templateUrl: function (element, attributes) {
                return attributes.template;
            },
            controller: ['$scope', '$window', function ($scope, $window) {
                $scope.addTag = function () {
                    if($scope.tagForm.$invalid) {
                        return;
                    }

                    var tag = {
                        name: $scope.newTagKey,
                        value: $scope.newTagValue,
                    };

                    if($scope.autoscale) {
                        tag.propagate_at_launch = !!$scope.newTagPropagate;
                    }

                    $scope.tags.push(tag);

                    resetForm();
                    $scope.$emit('tagUpdate');
                };

                $scope.removeTag = function ($index) {
                    $scope.tags.splice($index, 1);
                    $scope.$emit('tagUpdate');
                };

                var containsKey = function (collection, key) {
                    return collection.some(function (current) {
                        return current.name === key;
                    });
                };

                var resetForm = function () {
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
            }],
            link: function (scope, element, attrs, ctrl, transcludeContents) {
                var content = transcludeContents();
                var tags = JSON.parse(content.text() || '{}');
                scope.tags = tags.filter(function (current) {
                    return !current.name.match(/^aws:.*/) &&
                        !current.name.match(/^euca:.*/);
                });

                attrs.showNameTag = !attrs.showNameTag; // default to true
                attrs.autoscale = !!attrs.autoscale;    // default to false

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
    .directive('preventDuplicates', function () {
        return {
            require: 'ngModel',
            restrict: 'A',
            link: function (scope, element, attrs, ctrl) {
                ctrl.$validators.preventDuplicates = function (modelValue, viewValue) {
                    return !scope.tags.some(function (current) {
                        return viewValue === current.name;
                    });
                };
            }
        };
    })
    .filter('safe', ['$sanitize', function ($sanitize) {
        return function (tag) {
            return $sanitize(tag.name + ' = ' + tag.value);
        };
    }]);
