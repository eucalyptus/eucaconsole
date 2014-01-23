/**
 * @fileOverview Scaling Group detail page JS
 * @requires AngularJS
 *
 */

// Volume page includes the AutoScale tag editor, so pull in that module as well.
angular.module('ScalingGroupPage', ['AutoScaleTagEditor'])
    .controller('ScalingGroupPageCtrl', function ($scope) {
        $scope.minSize = 1;
        $scope.desiredCapacity = 1;
        $scope.maxSize = 1;
        $scope.initChosenSelectors = function () {
            $('#launch_config').chosen({'width': '60%', search_contains: true});
            $('#availability_zones').chosen({'width': '80%', search_contains: true});
            $('#load_balancers').chosen({'width': '80%', search_contains: true});
            $('#termination_policies').chosen({'width': '80%', search_contains: true});
        };
        $scope.setInitialValues = function () {
            $scope.minSize = parseInt($('#min_size').val(), 10);
            $scope.desiredCapacity = parseInt($('#desired_capacity').val(), 10);
            $scope.maxSize = parseInt($('#max_size').val(), 10);
        };
        $scope.initController = function () {
            $scope.setInitialValues();
            $scope.initChosenSelectors();
        };
        $scope.handleSizeChange = function () {
            // Adjust desired/max based on min size change
            if ($scope.desiredCapacity < $scope.minSize) {
                $scope.desiredCapacity = $scope.minSize;
            }
            if ($scope.maxSize < $scope.desiredCapacity) {
                $scope.maxSize = $scope.desiredCapacity;
            }
        };
    })
;

