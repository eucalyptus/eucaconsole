/**
 * @fileOverview Launch Instance page JS
 * @requires AngularJS
 *
 */

// Launch Instance page includes the tag editor, so pull in that module as well.
angular.module('LaunchInstance', ['TagEditor'])
    .controller('LaunchInstanceCtrl', function ($scope) {
        $scope.form = $('#launch-instance-form');
        $scope.visitStep = function (step, $event) {
            $scope.form.trigger('validate');
            var invalidFields = $scope.form.find('[data-invalid]');
            if (invalidFields.length) {
                invalidFields.focus();
                $event.preventDefault();
                return false;
            }
            $('#tabStep' + step).click();
        };
    })
;

