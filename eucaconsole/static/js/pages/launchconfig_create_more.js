/**
 * @fileOverview Launchconfig create more like this launchconfig page JS
 * @requires AngularJS
 *
 */

// Launchconfig create-more-like page includes the Block Device Mapping editor
angular.module('LaunchconfigMore', ['BlockDeviceMappingEditor', 'EucaConsoleUtils'])
    .controller('LaunchconfigMoreCtrl', function ($scope, $timeout, eucaUnescapeJson) {
        $scope.expanded = false;
        $scope.toggleContent = function () {
            $scope.expanded = !$scope.expanded;
        };
        $scope.initController = function (optionsJson) {
            $('#securitygroup').chosen({'width': '100%', search_contains: true});
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            var userData = options.user_data;
            if (userData.type !== '') {
                if (userData.type.indexOf('text') === 0) {
                    $scope.isFileUserData = false;
                    $("#userdata:not([display='none'])").val(userData.data);
                    $scope.inputtype = 'text';
                } else {
                    $scope.isFileUserData = true;
                    $("#userdatatype:not([display='none'])").text(userData.type);
                    $scope.inputtype = 'file';
                }
            }
            $scope.$watch('inputtype', function(newVal, oldVal) {
                if ($scope.inputtype == 'text' && newVal !== oldVal) {
                    $timeout(function() {
                        $('#userdata').focus();
                    });
                }
            });
        };
        $scope.isFormValid = function () {
            if (!$scope.launchconfigName || $('#name.ng-invalid').length > 0) {
                return false;
            }
            return true;
        };
    })
;

