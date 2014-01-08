/**
 * @fileOverview Scaling Group detail page JS
 * @requires AngularJS
 *
 */

// Volume page includes the AutoScale tag editor, so pull in that module as well.
angular.module('ScalingGroupPage', ['AutoScaleTagEditor'])
    .controller('ScalingGroupPageCtrl', function ($scope) {
        $scope.initChosenSelectors = function () {
            $('#launch_config').chosen({'width': '60%'});
            $('#availability_zones').chosen({'width': '80%'});
        };
        $scope.initController = function () {
            $scope.initChosenSelectors();
        };
    })
;

