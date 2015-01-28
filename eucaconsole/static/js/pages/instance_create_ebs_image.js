/**
 * @fileOverview Create image from instance page JS
 * @requires AngularJS
 *
 */

// Create Image page includes the Tag Editor and the Block Device Mapping editor
angular.module('InstanceCreateImage', ['TagEditor', 'BlockDeviceMappingEditor'])
    .controller('InstanceCreateImageCtrl', function ($scope, $timeout) {
        $scope.form = $('#create-image-form');
        $scope.expanded = false;
        $scope.name = '';
        $scope.isNotValid = true;
        $scope.toggleContent = function () {
            $scope.expanded = !$scope.expanded;
        };
        $scope.initController = function () {
            $scope.$watch('name', function () {
                if( $scope.name === undefined ){
                    $('#error').removeClass('hide');
                    $scope.isNotValid = true;
                }else{
                    $('#error').addClass('hide');
                    $scope.isNotValid = false;
                }
            });
        };
        $scope.checkRequiredInput = function () {
            $scope.isNotValid = false;
            if ($scope.name == '') {
                $scope.isNotValid = true;
            }
        };
        $scope.submitCreateImage = function() {
            $scope.checkRequiredInput();
            if (!$scope.isNotValid) { 
                $('#instance-shutdown-warn-modal').foundation('reveal', 'open');
            }
        };
        $scope.submitCreate = function() {
            $('#instance-shutdown-warn-modal').foundation('reveal', 'close');
            $scope.form.submit();
        };
    })
;

