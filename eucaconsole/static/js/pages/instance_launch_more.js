/**
 * @fileOverview Launch more like this instance page JS
 * @requires AngularJS
 *
 */

// Launch Instance page includes the Tag Editor, the Image Picker, and the Block Device Mapping editor
angular.module('LaunchMoreInstances', ['BlockDeviceMappingEditor'])
    .controller('LaunchMoreInstancesCtrl', function ($scope) {
        $scope.form = $('#launch-more-form');
        $scope.instanceNumber = 1;
        $scope.expanded = false;
        $scope.toggleContent = function () {
            $scope.expanded = !$scope.expanded;
        };
        $scope.setInitialValues = function () {
            $('#number').val($scope.instanceNumber);
        };
        $scope.initController = function () {
            $scope.setInitialValues();
            $(document).on('input', 'textarea', function () {  // userdata text
                $scope.intputtype = 'text';
                $scope.$apply();
            });
            $('#userdata_file').on('change', function () {  // userdata file
                $scope.intputtype = 'file';
                $scope.$apply();
            });
        };
        $scope.buildNumberList = function (limit) {
            // Return a 1-based list of integers of a given size ([1, 2, ... limit])
            limit = parseInt(limit, 10);
            var result = [];
            for (var i = 1; i <= limit; i++) {
                result.push(i);
            }
            return result;
        };
    })
;

