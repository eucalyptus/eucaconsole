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
        $scope.s3BucketError = false;
        $scope.s3PrefixError = false;
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
                create_with_enter: true,
                create_option_text: 'Create Bucket'
            });
            $scope.setWatch();
        };
        $scope.checkRequiredInput = function () {
            $scope.isNotValid = false;
            if ($scope.name == '' || $scope.s3_bucket == '' || $scope.s3_prefix == '' ) {
                $scope.isNotValid = true;
            } else if ($scope.s3BucketError || $scope.s3PrefixError) {
                $scope.isNotValid = true;
            }
        };
        $scope.validateS3BucketInput = function () {
            var re = /^[a-z0-9-\.]+$/;
            if ($scope.s3_bucket == '' || $scope.s3_bucket.match(re)) {
                $scope.s3BucketError = false;
            } else { 
                $scope.s3BucketError = true;
            }
        };
        $scope.validateS3PrefixInput = function () {
            var re = /^[a-z0-9-\.]+$/;
            if ($scope.s3_prefix == '' || $scope.s3_prefix.match(re)) {
                $scope.s3PrefixError = false;
            } else { 
                $scope.s3PrefixError = true;
            }
        };
        $scope.setWatch = function () {
            $scope.$watch('name', function () {
                $scope.checkRequiredInput();
            });
            $scope.$watch('s3_bucket', function () {
                $scope.validateS3BucketInput();
                $scope.checkRequiredInput();
            });
            $scope.$watch('s3_prefix', function () {
                $scope.validateS3PrefixInput();
                $scope.checkRequiredInput();
            });
            $scope.$watch('s3BucketError', function () {
                $('div#controls_s3_bucket').removeClass('error');
                if ($scope.s3BucketError) {
                    $('div#controls_s3_bucket').addClass('error');
                }
            });
            $scope.$watch('s3PrefixError', function () {
                $('div#controls_s3_prefix').removeClass('error');
                if ($scope.s3PrefixError) {
                    $('div#controls_s3_prefix').addClass('error');
                }
            });
        };
        $scope.submitCreate = function() {
            var pass = $('#bundle-password').val();
            $scope.form.find('#password').val(pass);
            $('#instance-shutdown-warn-modal').foundation('reveal', 'close');
            $scope.form.submit();
        };
    })
;

