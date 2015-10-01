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
                    $scope.tags.push({
                        name: $scope.newTagKey,
                        value: $scope.newTagValue,
                        propagate_at_launch: !!$scope.newTagPropagate
                    });
                };
                $scope.removeTag = function ($index) {
                    $scope.tags.splice($index, 1);
                };
            }],
            link: function (scope, element, attrs, ctrl, transclude) {
                var content = transclude();
                scope.tags = JSON.parse(content.text());

                if(!attrs.showNameTag) {
                    attrs.showNameTag = true;
                }
            }
        };
    }])
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