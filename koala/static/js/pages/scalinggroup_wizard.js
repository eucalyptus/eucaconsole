/**
 * @fileOverview Create Scaling Group wizard page JS
 * @requires AngularJS
 *
 */

// Scaling Group wizard includes the AutoScale Tag Editor
angular.module('ScalingGroupWizard', ['AutoScaleTagEditor'])
    .controller('ScalingGroupWizardCtrl', function ($scope) {
        $scope.form = $('#scalinggroup-wizard-form');
        $scope.initController = function () {
            // TODO: implement
        };
    })
;

