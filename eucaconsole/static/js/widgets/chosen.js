angular.module('EucaChosenModule', [])
.directive('chosen', function () {
    return {
        scope: {
            model: '=ngModel'
        },
        restrict: 'A',
        require: 'ngModel',
        link: function (scope, element, attrs, ctrl) {
            var chosenAttrs = JSON.parse(attrs.chosen || '{}');
            for(var key in attrs) {
                if(/^chosen-.*/.test(key)) {
                    chosenAttrs[key] = attrs[key];
                }
            }
            element.chosen(chosenAttrs);

            element.on('change', function () {
                scope.validateField(this);
            });
        },
        controller: ['$scope', '$element', function ($scope, $element) {
            $scope.validateField = function (element) {
                var isValid = element[0].selectedIndex > -1,
                    form = this.form && this.form.name,
                    field = this.name;

                if(form && field) {
                    $scope[form][field].$setValidity('required', isValid);
                }
            };

            $scope.$watch('model', function () {
                $scope.validateField($element);
            });
        }]
    };
});
