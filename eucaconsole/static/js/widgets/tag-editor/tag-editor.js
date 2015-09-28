angular.module('TagEditorModule', [])
    .directive('fuckingTagEditor', function () {
        return {
            /*
            restrict: 'E',
            templateUrl: function (element, attributes) {
                return attributes.template;
            },
            */
            template: '<div>{{ editor }}</div>',
            controller: ['$scope', function ($scope) {
                console.log($scope.template);
                $scope.editor = 'EDITOR!!!';
            }],
            link: function () {
                console.log('linking');
            }
        };
    });