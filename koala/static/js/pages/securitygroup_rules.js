/**
 * @fileOverview Security Group rules editor JS
 * @requires AngularJS
 *
 */

angular.module('SecurityGroupRules', [])
    .controller('SecurityGroupRulesCtrl', function ($scope) {
        $scope.rulesEditor = $('#rules-editor');
        $scope.rulesTextarea = $scope.rulesEditor.find('textarea#rules');
        $scope.rulesArray = [];
        $scope.fromPort = '';
        $scope.toPort = '';
        $scope.syncRules = function () {
            $scope.rulesTextarea.val(JSON.stringify($scope.rulesArray));
        };
        $scope.initRules = function(rulesArray) {
            // Get existing rules and shove into scope
            $scope.rulesArray = JSON.parse(rulesArray);
            $scope.syncRules();
        };
        $scope.removeRule = function (index, $event) {
            $event.preventDefault();
            $scope.rulesArray.splice(index, 1);
            $scope.syncRules();
        };
        $scope.addRule = function ($event) {

        };
        $scope.setPorts = function(port) {
            if (!isNaN(port)) {
                $scope.fromPort = port;
                $scope.toPort = port;
            } else {
                $scope.fromPort = $scope.toPort = '';
                $('.port.from').focus();
            }
        }
    })
;


// Avoid clobbering the tag editor, since we have multiple ng-app="" attributes on the page.
angular.element(document).ready(function() {
    angular.bootstrap(document.getElementById('tag-editor'), ['TagEditor']);
});

