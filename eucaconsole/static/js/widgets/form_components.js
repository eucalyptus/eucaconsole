/**
 * @fileOverview Directives and extensions for forms
 * @requires AngularJS
 *
 */

angular.module('FormComponents', [])
    .directive('reserved', function () {
        /**
         * Validator
         * Enforce adherence to a reserved-words list on a form input.
         *
         * Usage: Add as an attribute to a form input field with a space-separated list
         * of words that must not be accepted by this input.
         *
         * If a 'case-insensitive' attribute is present on the input field, a case-insensitive match
         * is made.
         **/
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function (scope, element, attrs, ctrl) {
                var reserved = attrs.reserved.split(/\s+/),
                    flags = ('caseInsensitive' in attrs) ? 'i' : '';

                ctrl.$validators.reserved = function (modelValue) {
                    return !reserved.some(function (term) {
                        var re = new RegExp(term, flags);
                        return re.test(modelValue);
                    });
                };
            }
        };
    })
    .directive('match', function () {
        /**
         * Validator
         * Enforce that the content of an input field must match the content of a value on $scope.
         *
         * Usage: Add as an attribute to a form input field with the name of a value on $scope.
         */
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function (scope, element, attrs, ctrl) {
                var target = attrs.match;

                ctrl.$validators.match = function (modelValue) {
                    if(ctrl.$isEmpty(modelValue)) {
                        return true;
                    }
                    return modelValue === scope[target];
                };
            }
        };
    })
    .directive('nomatch', function () {
        /**
         * Validator
         * Enforce that the content of an input field must NOT match the content of a value on $scope.
         *
         * Usage: Add as an attribute to a form input field with the name of a value on $scope.
         */
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function (scope, element, attrs, ctrl) {
                var target = attrs.nomatch;

                ctrl.$validators.nomatch = function (modelValue) {
                    if(ctrl.$isEmpty(modelValue)) {
                        return true;
                    }
                    return modelValue !== scope[target];
                };
            }
        };
    });
