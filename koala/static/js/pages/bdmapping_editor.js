/**
 * @fileOverview Block Device Mapping Editor JS
 * @requires AngularJS
 *
 */
angular.module('BlockDeviceMappingEditor', [])
    .controller('BlockDeviceMappingEditorCtrl', function ($scope) {
        $scope.bdmTextarea = $('#bdmapping');
        $scope.bdMapping = {};
        $scope.initBlockDeviceMappingEditor = function (bdmJson) {
            bdmJson = bdmJson || "{}";
            $scope.bdMapping = JSON.parse(bdmJson);
            $scope.bdmTextarea.val(bdmJson);
        };
    })
;
