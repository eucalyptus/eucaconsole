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
        $scope.syncRules = function () {
            $scope.rulesTextarea.val(JSON.stringify($scope.rulesArray));
        };
        $scope.initRules = function(rulesArray) {
            // Get existing rules and shove into scope
            $scope.rulesArray = JSON.parse(rulesArray);
            $scope.syncRules();
        };
        $scope.updateRuleKey = function (index, $event) {

        };
        $scope.updateRuleValue = function (index, $event) {

        };
        $scope.removeRule = function (index) {

        };
        $scope.addRule = function ($event) {

        };
    })
;


// Avoid clobbering the tag editor, since we have multiple ng-app="" attributes on the page.
angular.element(document).ready(function() {
    angular.bootstrap(document.getElementById('tag-editor'), ['TagEditor']);
});

