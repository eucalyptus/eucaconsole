/**
 * @fileOverview Create image from instance page JS
 * @requires AngularJS
 *
 */

// Create Image page includes the Tag Editor and the Block Device Mapping editor
angular.module('InstanceCreateImage', ['TagEditor', 'BlockDeviceMappingEditor'])
    .controller('InstanceCreateImageCtrl', function ($scope) {
        $scope.form = $('#create-image-form');
        $scope.expanded = false;
        $scope.toggleContent = function () {
            $scope.expanded = !$scope.expanded;
        };
        $scope.initController = function () {

        };
    })
;

