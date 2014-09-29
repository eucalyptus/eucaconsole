/**
 * @fileOverview Create image from instance page JS
 * @requires AngularJS
 *
 */

// Create Image page includes the Tag Editor 
angular.module('InstanceCreateImage', ['TagEditor'])
    .controller('InstanceCreateImageCtrl', function ($scope, $timeout) {
        $scope.form = $('#create-image-form');
        $scope.expanded = false;
        $scope.name = '';
        $scope.s3_bucket = '';
        $scope.s3_prefix = 'image';
        $scope.isNotValid = true;
        $scope.toggleContent = function () {
            $scope.expanded = !$scope.expanded;
        };
        $scope.initController = function () {
            $('#s3_bucket').chosen({search_contains: true, create_option: function(term){
                    var chosen = this;
                    var bucket_name = term;
                    $timeout(function() {
                        chosen.append_option({
                            value: bucket_name,
                            text: bucket_name
                        });
                    });
                },
                create_option_text: 'Create Bucket',
            });
            $scope.$watch('name', function () {
                $scope.checkRequiredInput();
            });
            $scope.$watch('s3_bucket', function () {
                $scope.checkRequiredInput();
            });
            $scope.$watch('s3_prefix', function () {
                $scope.checkRequiredInput();
            });
        };
        $scope.checkRequiredInput = function () {
            if ($scope.name == '' || $scope.s3_bucket == '' || $scope.s3_prefix == '' ) {
                $scope.isNotValid = true;
            } else {
                $scope.isNotValid = false;
            }
        };
        $scope.submitCreate = function() {
            var pass = $('#bundle-password').val();
            $scope.form.find('#password').val(pass);
            $('#instance-shutdown-warn-modal').foundation('reveal', 'close');
            $scope.form.submit();
        };
    })
;

