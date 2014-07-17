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
            $('#s3-bucket').chosen({'width': '50%', search_contains: true, create_option: function(term){
                    var chosen = this;
                    // validate the entry
                    var bucket_name = term;
                    // ensure it has matches appropriate pattern
                    $timeout(function() {
                        chosen.append_option({
                            value: term,
                            text: term
                        });
                    });
                },
                create_option_text: 'Create Bucket',
            });
        };
        $scope.submitCreate = function() {
            $('#instance-shutdown-warn-modal').foundation('reveal', 'close');
            $scope.form.submit();
        };
    })
;

